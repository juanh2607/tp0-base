import socket
import logging
import signal
from typing import List, Dict, Any
from common.betting_protocol import (
    receive_message,
    STORE_BET,
    STORE_BATCH,
    FIN,
    END_BETS,
    SYN,
)
from common.utils import store_bets, Bet
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
            logging.info("action: shutdown | result: success")
        except OSError as e:
            logging.info(f"action: closing_listener | result: fail | error: {e}")
            logging.info("action: shutdown | result: fail")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        clients_received = 0

        while self._running and clients_received < self._clients:
            client_sock = self.__accept_new_connection()
            if client_sock:
                clients_received += 1
                self.__handle_client_connection(client_sock)

        logging.info("action: sorteo | result: success")

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
                    break
                elif msg == SYN:
                    logging.info(
                        f"action: SYN_received | result: success | agency_id: {data}"
                    )
                    send_message_with_length(client_sock, "ok")
                else:
                    raise ValueError(f"Unknown message received: {msg}")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        # finally:
        #     client_sock.close()

    def __handle_store_bet(self, client_sock: socket.socket, bet: Bet):
        """Stores the bets and sends a response to the client if successful"""
        store_bets([bet])

        # Send a response back to the client
        send_message_with_length(client_sock, "ok")
        logging.info(
            f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}"
        )

    def __handle_store_batch(
        self, client_sock: socket.socket, batch: List[Bet], err: Dict[str, Any]
    ):
        store_bets(batch)

        if err:
            logging.info(
                f"action: apuesta_recibida | result: failed | cantidad: {len(batch)}"
            )

        logging.info(
            f"action: apuesta_recibida | result: success | cantidad: {len(batch)}"
        )

        # Send a response back to the client
        send_message_with_length(client_sock, "ok")
