import socket
import logging
import signal
import threading
from typing import List, Dict, Any
from common.betting_protocol import (
    receive_message,
    send_winners,
    STORE_BET,
    STORE_BATCH,
    FIN,
    END_BETS,
    SYN,
)
from common.utils import store_bets, Bet, load_bets, has_won
from common.serializer import send_message_with_length


class Server:
    def __init__(
        self,
        port: int,
        listen_backlog: int,
        clients: int,
    ):
        """
        Args:
            `port`: where the server will be listening for new connections.
            `listen_backlog`: max amount of pending connections before being accepted.
            `clients`: the amount of clients the server is expected to handle.
        """

        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen(listen_backlog)
        self._running: bool = True

        assert 0 < clients and clients <= 5
        self._clients = clients
        self.__ended_clients = 0

        self._clients_sockets: Dict[int, socket.socket] = {}

        # Key: Agency, Value: List of DNIs of the winners
        self._winners: Dict[int, List[str]] = {}

        # Lock used to protect the betting file from concurrent access
        self._bets_file_lock = threading.Lock()

        # Signal handlers
        # SIGTERM is the standard signal for requesting a process to terminate gracefully.
        signal.signal(signal.SIGTERM, self.handle_signal)
        # SIGINT is the signal received when the user presses `CTRL + C` in the terminal.
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, signum, frame):
        """Handle termination signals for graceful shutdown"""
        logging.info("action: shutdown | result: in_progress")
        self._running = False
        try:
            self._server_socket.close()
            logging.info("action: closing_listener | result: success")
            for agency_id, client_sock in self._clients_sockets.items():
                client_sock.close()
                logging.info(
                    f"action: closing_socket | agency_id: {agency_id} | result: success"
                )
            logging.info("action: shutdown | result: success")
        except OSError as e:
            logging.info(f"action: closing_listener | result: fail | error: {e}")
            logging.info("action: shutdown | result: fail")

    def run(self):
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                if client_sock:
                    threading.Thread(
                        target=self.__handle_client_connection,
                        args=(client_sock,),
                        daemon=True,  # Wait for threads to close when program ends
                    ).start()
            except Exception as e:
                logging.error(f"Error accepting new connection: {e}")

    def __accept_new_connection(self) -> socket.socket:
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        try:
            logging.info("action: accept_connections | result: in_progress")
            c, addr = self._server_socket.accept()
            logging.info(
                f"action: accept_connections | result: success | ip: {addr[0]}"
            )
            return c
        except OSError:
            return None  # server socket is closed

    def __handle_client_connection(self, client_sock: socket.socket):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                msg, data, err = receive_message(client_sock)

                if msg == STORE_BET:
                    self.__handle_store_bet(client_sock, data)
                elif msg == STORE_BATCH:
                    self.__handle_store_batch(client_sock, data, err)
                elif msg == FIN:
                    break
                elif msg == END_BETS:
                    self.__handle_end_bets()
                    break
                elif msg == SYN:
                    self.__handle_syn(client_sock, data)
                else:
                    raise ValueError(f"Unknown message received: {msg}")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")

    def __handle_store_bet(self, client_sock: socket.socket, bet: Bet):
        """Stores the bets and sends a response to the client if successful"""
        with self._bets_file_lock:
            store_bets([bet])

        # Send a response back to the client
        send_message_with_length(client_sock, "ok")
        logging.info(
            f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}"
        )

    def __handle_store_batch(
        self, client_sock: socket.socket, batch: List[Bet], err: Dict[str, Any]
    ):
        with self._bets_file_lock:
            store_bets(batch)

        if err:
            logging.info(
                f"action: apuesta_recibida | result: failed | cantidad: {len(batch)}"
            )

        logging.info(
            f"action: apuesta_recibida | result: success | cantidad: {len(batch)}"
        )

        send_message_with_length(client_sock, "ok")

    def __handle_syn(self, client_sock: socket.socket, agency_id: int):
        """Saves the conection with the client and responds with an 'ok'"""
        self._clients_sockets[agency_id] = client_sock

        logging.info(f"action: SYN_received | result: success | agency_id: {agency_id}")

        send_message_with_length(client_sock, "ok")

    def __handle_end_bets(self):
        self.__ended_clients += 1
        if self.__ended_clients == self._clients:
            self.__run_lottery()

    def __run_lottery(self):
        logging.info("action: sorteo | result: success")

        with self._bets_file_lock:
            for bet in load_bets():
                if has_won(bet):
                    if bet.agency not in self._winners:
                        self._winners[bet.agency] = []

                    self._winners[bet.agency].append(bet.document)

        for agency_id, client_sock in self._clients_sockets.items():
            try:
                send_winners(client_sock, self._winners.get(agency_id, []))
                client_sock.close()
            except OSError as e:
                logging.error(
                    f"action: close_socket | result: fail | agency_id: {agency_id} | error: {e}"
                )

        self._clients_sockets = {}
