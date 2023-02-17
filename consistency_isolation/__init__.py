import socket
import telnetlib
import threading


class Client:
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


class Server:
    def __init__(self, sock: socket.socket):
        self._telnet = telnetlib.Telnet()
        self._telnet.sock = sock

    def readline(self) -> str:
        self._telnet.write("db> ".encode())
        msg = self._telnet.read_until("\r\n".encode()).decode().strip()
        return msg

    def send(self, msg: str) -> None:
        self._telnet.write(msg.encode() + b"\r\n")

    def close(self):
        self._telnet.sock.close()


class RWLock:
    def __init__(self):
        self._read_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._read_count = 0

    def acquire_read(self):
        with self._read_lock:
            self._read_count += 1
            if self._read_count == 1:
                self._write_lock.acquire()

    def release_read(self):
        with self._read_lock:
            self._read_count -= 1
            if self._read_count == 0:
                self._write_lock.release()

    def acquire_write(self):
        self._write_lock.acquire()

    def release_write(self):
        self._write_lock.release()
