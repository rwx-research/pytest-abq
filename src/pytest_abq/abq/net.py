from dataclasses import asdict
import typing as t
import socket
import json
import struct

from .types import (
    AbqNativeRunnerSpawnedMessage,
    InitSuccessMessage,
    ManifestSuccessMessage,
    TestResultMessage,
)

ENCODING_U32_BE = ">I"


def protocol_write(
    sock: socket.socket,
    data: t.Union[
        AbqNativeRunnerSpawnedMessage,
        ManifestSuccessMessage,
        InitSuccessMessage,
        TestResultMessage,
    ],
):
    """
    Writes an ABQ data value to a socket stream.
    """
    msg = json.dumps(data).encode("utf-8")
    msg_header = struct.pack(ENCODING_U32_BE, len(msg))
    sock.sendall(msg_header)
    sock.sendall(msg)


def read_exact(sock: socket.socket, size: int) -> bytearray:
    buf = bytearray(size)
    read = 0
    while read < size:
        add_read = sock.recv_into(memoryview(buf)[read:])
        if add_read == 0:
            raise EOFError
        read += add_read
    return buf


def protocol_read(sock: socket.socket) -> t.Any:
    """
    Read an ABQ data value from a socket stream.
    """
    (size,) = struct.unpack(ENCODING_U32_BE, read_exact(sock, 4))
    data = read_exact(sock, size)
    return json.loads(data)
