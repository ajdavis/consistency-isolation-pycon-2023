import socket
import telnetlib


class Client:
    def __init__(self):
        self._telnet: telnetlib.Telnet | None = None

    def readline(self) -> str:
        self._ensure_connected()
        return self._telnet.read_until("\r\n".encode()).decode().strip()

    def write(self, msg: str) -> None:
        self._ensure_connected()
        self._telnet.read_until("db> ".encode())  # Await prompt.
        self._telnet.write(msg.encode() + b"\r\n")

    def _ensure_connected(self) -> None:
        if self._telnet is None:
            self._telnet = telnetlib.Telnet("localhost")


class Server:
    def __init__(self, sock: socket.socket):
        self._telnet = telnetlib.Telnet()
        self._telnet.sock = sock

    def readline(self) -> str:
        self._telnet.write("db> ".encode())
        msg = self._telnet.read_until("\r\n".encode()).decode().strip()
        return msg

    def write(self, msg: str) -> None:
        self._telnet.write(msg.encode() + b"\r\n")

    def close(self):
        self._telnet.sock.close()

