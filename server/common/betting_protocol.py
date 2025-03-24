import socket
import logging
from typing import Tuple, Any
from common.serializer import (
    deserialize_message,
    deserialize_bet,
    deserialize_batch,
)

STORE_BET = 1
STORE_BATCH = 2
FIN = 3

MESSAGE_IDS = {STORE_BET: "STORE_BET", STORE_BATCH: "STORE_BATCH", FIN: "FIN"}


def receive_message(client_sock: socket.socket) -> Tuple[int, Any]:
    """
    Returns a tuple with:
        * [0]: the msg id
        * [1]: the data, if any, that comes with the message
    """
    try:
        msg, data = deserialize_message(client_sock)

        addr = client_sock.getpeername()
        logging.info(
            f"action: receive_message | result: success | ip: {addr[0]} | msg: {MESSAGE_IDS[msg]}"
        )

        if msg == STORE_BET:
            return msg, deserialize_bet(data)
        elif msg == STORE_BATCH:
            return msg, deserialize_batch(data)
        elif msg == FIN:
            return msg, None
        else:
            raise ValueError(f"Unknown message received: {msg}")

    except Exception as e:
        logging.error(f"Error while receiving and deserializing message: {e}")
        return None
