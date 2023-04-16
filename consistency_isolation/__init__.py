import dataclasses
import os.path
import re
import socket
import sys
import telnetlib
import threading
from collections.abc import Callable


class ClientConnection:
    def __init__(self):
        self._telnet: telnetlib.Telnet | None = None

    def readline(self) -> str:
        self._ensure_connected()
        return self._telnet.read_until("\r\n".encode()).decode().strip()

    def send(self, msg: str) -> None:
        self._ensure_connected()
        self._telnet.read_until("db> ".encode())  # Await prompt.
        self._telnet.write(msg.encode() + b"\r\n")

    def _ensure_connected(self) -> None:
        if self._telnet is None:
            self._telnet = telnetlib.Telnet("localhost")


@dataclasses.dataclass
class Command:
    name: str
    key: None | str = None
    value: None | str = None


class ServerConnection:
    def __init__(self, sock: socket.socket):
        self._telnet = telnetlib.Telnet()
        self._telnet.sock = sock
        self._client_addr = sock.getpeername()
        print(f"{self._client_addr} connected")
        program = f"{os.path.basename(os.path.dirname(sys.argv[0]))}" \
                  f"/{os.path.basename(sys.argv[0])}"
        self.send(f"Welcome to {program}!\nType 'bye' to quit.")

    def readline(self) -> str | None:
        try:
            self._telnet.write("db> ".encode())
            return self._telnet.read_until("\r\n".encode()).decode().strip()
        except (EOFError, ConnectionResetError):
            print(f"{self._client_addr} disconnected")
            self._telnet.sock.close()
            return None

    def next_command(self) -> Command | None:
        while True:
            msg = self.readline()
            if msg is None:
                return None
            elif msg in ("commit", "bye"):
                return Command(msg)
            elif match := re.match(
                r"(?P<name>get|set)\s+(?P<key>\S+)(\s+(?P<value>\S+))?",
                msg):
                return Command(**match.groupdict())

            self.send("invalid syntax")
            # Loop around and try again.

    def send(self, msg: str) -> None:
        self._telnet.write(msg.encode() + b"\r\n")

    def close(self):
        self._telnet.sock.close()


class Server:
    def __init__(self):
        self._sock: socket.socket | None = None

    def serve(self, worker_fn: Callable[[ServerConnection], None]):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(('', 23), )
        self._sock.listen(10)

        while True:
            sock, addr = self._sock.accept()
            server = ServerConnection(sock)

            def work_then_close(sc: ServerConnection):
                try:
                    worker_fn(sc)
                finally:
                    sc.close()

            threading.Thread(target=work_then_close, args=(server,)).start()
