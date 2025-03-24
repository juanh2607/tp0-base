import socket
import logging
from common.utils import store_bets
from common.serializer import (
    deserialize_message,
    deserialize_bet,
    send_message_with_length,
)

MESSAGE_IDS = {
    1: "STORE_BET",
}

STORE_BET = 1


def receive_message(client_sock: socket.socket):
    try:
        msg, data = deserialize_message(client_sock)

        addr = client_sock.getpeername()
        logging.info(
            f"action: receive_message | result: success | ip: {addr[0]} | msg: {MESSAGE_IDS[msg]}"
        )

        if msg == STORE_BET:
            handle_store_bet(client_sock, data)
        else:
            raise ValueError(f"Unknown message received: {msg}")

    except Exception as e:
        logging.error(f"Error while receiving and deserializing message: {e}")
        return None


def handle_store_bet(client_sock: socket.socket, data: bytes):
    """Stores the bets and sends a response to the client if successful"""
    bet = deserialize_bet(data)

    store_bets([bet])

    # Send a response back to the client
    send_message_with_length(client_sock, "ok")
    logging.info(
        f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}"
    )
