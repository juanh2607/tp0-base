import socket
import logging
import signal
from common.utils import Bet, store_bets


class Server:
    def __init__(self, port: int, listen_backlog: int):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen(listen_backlog)
        self._running: bool = True

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

        while self._running:
            client_sock = self.__accept_new_connection()
            if client_sock:
                self.__handle_client_connection(client_sock)

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
            msg = self.__receive_message(client_sock)
            if msg:
                addr = client_sock.getpeername()
                logging.info(
                    f"action: receive_message | result: success | ip: {addr[0]} | msg: {msg}"
                )

                store_bets([msg])
                # Send a response back to the client
                client_sock.send(f"Received\n".encode("utf-8"))
                logging.info(
                    f"action: apuesta_almacenada | result: success | dni: {msg.document} | numero: {msg.number}"
                )

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __receive_message(self, client_sock: socket.socket) -> Bet:
        """Receive and deserialize the message from the client."""
        try:
            # Read first int32 with total data length in bytes
            total_length_bytes = client_sock.recv(4)
            if not total_length_bytes:
                return None

            total_length = int.from_bytes(total_length_bytes, byteorder="big")

            data: bytes = b""
            received = 0

            # Read each field as <length_field: i32><field: str>
            while received < total_length:
                length_bytes = client_sock.recv(4)
                if not length_bytes:
                    break

                field_length = int.from_bytes(length_bytes, byteorder="big")
                field_data = client_sock.recv(field_length)
                if not field_data:
                    break

                data += length_bytes
                data += field_data
                received += 4 + field_length

            return self.__deserialize_bet(data)

        except Exception as e:
            logging.error(f"Error while receiving and deserializing message: {e}")
            return None

    def __deserialize_bet(self, data: bytes) -> Bet:
        fields = []
        index = 0

        while index < len(data):
            length = int.from_bytes(data[index : index + 4], byteorder="big")
            index += 4

            field = data[index : index + length].decode("utf-8")
            index += length

            fields.append(field)

        bet = Bet(
            agency=fields[0],
            first_name=fields[1],
            last_name=fields[2],
            document=fields[3],
            birthdate=fields[4],
            number=fields[5],
        )

        return bet
