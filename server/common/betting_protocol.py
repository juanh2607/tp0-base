import socket
import logging
from typing import Tuple, Any
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
        else:
            raise ValueError(f"Unknown message received: {msg}")

    except Exception as e:
        logging.error(f"Error while receiving and deserializing message: {e}")
        return None
