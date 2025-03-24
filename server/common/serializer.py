import socket
from typing import Tuple
from common.utils import Bet, recv_exactly, send_exactly


def deserialize_message(client_sock: socket.socket) -> Tuple[int, bytes]:
    """
    Returns a tuple with:
        * [0]: an int indicating the type of message received
        * [1]: data that comes with the message

    Can raise exceptions
    """
    # <msg id: u8><total_length: u32>
    msg_byte = recv_exactly(client_sock, 1)
    total_length_bytes = recv_exactly(client_sock, 4)

    msg = int.from_bytes(msg_byte, byteorder="big")
    total_length = int.from_bytes(total_length_bytes, byteorder="big")

    data = recv_exactly(client_sock, total_length)

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


def send_message_with_length(sock: socket.socket, message: str):
    """Send the message with the format <length: uint32><msg: str>"""
    data = message.encode("utf-8")

    length = len(data)
    length_bytes = length.to_bytes(4, byteorder="big")

    send_exactly(sock, length_bytes)
    send_exactly(sock, data)
