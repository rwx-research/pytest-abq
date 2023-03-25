import json
import socket
import struct
import threading
from typing import List, Tuple, Union

from pytest_abq.abq.net import protocol_read


def harness(data: List[bytes], expectations: List[str]):
    read_index = 0

    def asserter(server_conn):
        for expectation in expectations:
            msg = protocol_read(server_conn)
            assert (
                msg == expectation
            ), f"Expected: {expectations[read_index]}, got: {msg}"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 0))
    server_socket.listen(1)

    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_conn.connect(server_socket.getsockname())

    server_conn, _ = server_socket.accept()

    server_assert_thread = threading.Thread(target=asserter, args=(server_conn,))
    server_assert_thread.start()

    for chunk in data:
        client_conn.sendall(chunk)

    server_assert_thread.join()

    client_conn.close()
    server_socket.close()


# Helper functions
def to_u32be_len(s: str) -> bytes:
    return struct.pack(">I", len(s.encode("utf-8")))


def to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


# Test cases
def test_read_sized_message():
    msg1 = '"hello world"'
    data = [to_u32be_len(msg1) + to_bytes(msg1)]

    expectations = [json.loads(msg1)]

    harness(data, expectations)


def test_read_sized_unicode_message():
    msg1 = '"©ጷ€🎋"'
    data = [to_u32be_len(msg1) + to_bytes(msg1)]

    expectations = [json.loads(msg1)]

    harness(data, expectations)


def test_read_split_sized_message():
    msg1 = '"hello world"'
    data = [to_u32be_len(msg1), to_bytes(msg1)]

    expectations = [json.loads(msg1)]

    harness(data, expectations)


def test_read_multiple_sized_message():
    msg1 = '"hello world"'
    msg2 = '"mona lisa"'
    data = [to_u32be_len(msg1) + to_bytes(msg1) + to_u32be_len(msg2) + to_bytes(msg2)]

    expectations = [json.loads(msg1), json.loads(msg2)]

    harness(data, expectations)


def test_read_split_sized_message_multiple():
    msg1 = '"hello world"'
    data = [to_u32be_len(msg1), to_bytes('"hello '), to_bytes('world"')]

    expectations = [json.loads(msg1)]

    harness(data, expectations)


def test_read_split_message_size_and_split_message():
    msg1 = '"hello world"'
    msg_size_buf = to_u32be_len(msg1)
    data = [msg_size_buf[:2], msg_size_buf[2:], to_bytes('"hello '), to_bytes('world"')]

    expectations = [json.loads(msg1)]

    harness(data, expectations)


def test_read_multiple_messages_delivered_in_one_write():
    msg1 = '"hello world"'
    msg2 = '"mona lisa"'

    chunk = to_u32be_len(msg1) + to_bytes(msg1) + to_u32be_len(msg2) + to_bytes(msg2)
    data = [chunk]

    expectations = [json.loads(msg1), json.loads(msg2)]

    harness(data, expectations)


def test_read_multiple_messages_with_overlapping_write_sections():
    msg1 = '"hello world"'
    msg2 = '"mona lisa"'

    chunk1 = to_u32be_len(msg1) + to_bytes(msg1) + to_u32be_len(msg2)
    chunk2 = to_bytes(msg2)
    data = [chunk1, chunk2]

    expectations = [json.loads(msg1), json.loads(msg2)]

    harness(data, expectations)
