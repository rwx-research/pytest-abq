from dataclasses import dataclass
import os
import socket
import sys
import platform
import pytest
from typing import Literal, Union

from .types import (
    AbqNativeRunnerSpawnedMessage,
    Connection,
    NativeRunnerSpecification,
    ProtocolVersion,
)
from .net import protocol_write
from ..version import __version__

_abq_socket = os.environ.get("ABQ_SOCKET")
_host = None
_port = None
if _abq_socket is not None:
    _host, _port_s = _abq_socket.split(":")
    _port = int(_port_s)


spawned_message = AbqNativeRunnerSpawnedMessage(
    type="abq_native_runner_spawned",
    protocol_version=ProtocolVersion(type="abq_protocol_version", major=0, minor=2),
    runner_specification=NativeRunnerSpecification(
        type="abq_native_runner_specification",
        name="pytest_abq",
        version=__version__,
        test_framework="pytest",
        test_framework_version=pytest.__version__,
        language="Python",
        language_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        host=sys.implementation.cache_tag,
    ),
)


@dataclass
class EnabledConfig:
    enabled: Literal[True]
    host: str
    port: int
    should_generate_manifest: bool

    def connect(self) -> Connection:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        # ABQ sockets are local connections; no need for Nagle's, since it will
        # only slow traffic down.
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        protocol_write(sock, spawned_message)

        return sock


@dataclass
class DisabledCofig:
    enabled: Literal[False]


Config = Union[EnabledConfig, DisabledCofig]

if _host is not None and _port is not None:
    _config: Config = EnabledConfig(
        enabled=True,
        host=_host,
        port=_port,
        should_generate_manifest=(os.environ.get("ABQ_GENERATE_MANIFEST") == "1"),
    )
else:
    _config = DisabledCofig(
        enabled=False,
    )


def get_config() -> Config:
    return _config
