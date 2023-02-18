import re
import socket
import threading
from typing import TypeAlias

from .. import Server

Database: TypeAlias = dict[str, str]

db: Database = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 23), )
server_socket.listen(1)


def server_thread(sock: socket.socket, client_addr: tuple[str, int]):
    print(f"{client_addr} connected")
    server = Server(sock)
    server.send(f"Welcome to {__file__}!")
    txn: Database = {}
    while True:
        try:
            cmd = server.readline()
        except (EOFError, ConnectionResetError):
            break  # Disconnected.

        if cmd == "bye":
            server.send("bye")
            break
        elif match := re.match(r"set (\S+) (\S+)", cmd):
            txn[match.group(1)] = match.group(2)
        elif match := re.match(r"get (\S+)", cmd):
            key = match.group((1))
            try:
                # Read from local txn or fall back to global DB.
                server.send(txn[key] if key in txn else db[key])
            except KeyError:
                server.send("not found")
        elif cmd == "commit":
            db.update(txn)
            txn = {}
        else:
            server.send("invalid syntax")

    server.close()


while True:
    sock, addr = server_socket.accept()
    threading.Thread(target=server_thread, args=(sock, addr)).start()