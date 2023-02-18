import collections
import re
import socket
import threading
from typing import TypeAlias
from threading import RLock

from .. import Server

Database: TypeAlias = dict[str, str]

db: Database = {}
locks: dict[str, RLock] = collections.defaultdict(RLock)
metalock = threading.Lock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 23), )
server_socket.listen(1)


def server_thread(sock: socket.socket, client_addr: tuple[str, int]):
    print(f"{client_addr} connected")
    server = Server(sock)
    server.send(f"Welcome to {__file__}!")
    txn_locks = []

    def acquire_lock(k: str):
        with metalock:
            lock = locks[k]
        lock.acquire()
        txn_locks.append(lock)

    while True:
        try:
            cmd = server.readline()
        except (EOFError, ConnectionResetError):
            break  # Disconnected.

        if cmd == "bye":
            server.send("bye")
            break
        elif match := re.match(r"set (\S+) (\S+)", cmd):
            key = match.group((1))
            acquire_lock(key)
            db[key] = match.group(2)
        elif match := re.match(r"get (\S+)", cmd):
            key = match.group((1))
            acquire_lock(key)
            try:
                server.send(db[key])
            except KeyError:
                # Keep the RLock to prevent phantoms.
                server.send("not found")
        elif cmd == "commit":
            while txn_locks:
                txn_locks.pop().release()
        else:
            server.send("invalid syntax")

    # TODO: roll back the transaction and drop locks.
    assert not txn_locks
    print(f"{client_addr} disconnected")
    server.close()


while True:
    sock, addr = server_socket.accept()
    threading.Thread(target=server_thread, args=(sock, addr)).start()
