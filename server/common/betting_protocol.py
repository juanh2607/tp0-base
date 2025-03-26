import socket
import logging
from typing import Tuple, Any, Dict
from common.serializer import (
    deserialize_message,
    deserialize_bet,
    deserialize_batch,
    deserialize_syn,
)

STORE_BET = 1
STORE_BATCH = 2
FIN = 3
END_BETS = 4
SYN = 5

MESSAGE_IDS = {
    STORE_BET: "STORE_BET",
    STORE_BATCH: "STORE_BATCH",
    FIN: "FIN",
    END_BETS: "END_BETS",
    SYN: "SYN",
}


def receive_message(client_sock: socket.socket) -> Tuple[int, Any, Dict[str, Any]]:
    """
    Returns a tuple with:
        * [0]: the msg id
        * [1]: the data, if any, that comes with the message
        * [2]: a dictionary with errors
    """
    try:
        msg, data = deserialize_message(client_sock)
        addr = client_sock.getpeername()
        logging.info(
            f"action: receive_message | result: success | ip: {addr[0]} | msg: {MESSAGE_IDS[msg]}"
        )

        if msg == STORE_BET:
            return msg, deserialize_bet(data), {}
        elif msg == STORE_BATCH:
            data, err = deserialize_batch(data)
            return msg, data, err
        elif msg == FIN:
            return msg, None, {}
        elif msg == END_BETS:
            return msg, None, {}
        elif msg == SYN:
            return msg, deserialize_syn(data), {}
        else:
            raise ValueError(f"Unknown message received: {msg}")

    except ValueError as e:
        logging.error(e)
        return None, None, {}
    except Exception as e:
        logging.error(f"Error while receiving and deserializing message: {e}")
        return None, None, {}
