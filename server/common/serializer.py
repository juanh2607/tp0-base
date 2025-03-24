import socket
import logging
from typing import Tuple
from common.utils import Bet


def deserialize_message(client_sock: socket.socket) -> Tuple[int, bytes]:
    """
    Returns a tuple with:
        * [0]: an int indicating the type of message received
        * [1]: data that comes with the message

    Can raise exceptions
    """
    # <msg id: u8><total_length: u32>
    msg_byte = client_sock.recv(1)
    total_length_bytes = client_sock.recv(4)

    msg = int.from_bytes(msg_byte, byteorder="big")
    total_length = int.from_bytes(total_length_bytes, byteorder="big")

    data = client_sock.recv(total_length)

    return msg, data


def deserialize_bet(data: bytes) -> Bet:
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
