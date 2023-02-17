import collections
import re
import socket
import threading
from typing import TypeAlias

from .. import RWLock, Server

Database: TypeAlias = dict[str, str]

db: Database = {}
locks: dict[str, RWLock] = collections.defaultdict(RWLock)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 23), )
server_socket.listen(1)


def server_thread(sock: socket.socket, client_addr: tuple[str, int]):
    print(f"{client_addr} connected")
    server = Server(sock)
    server.send(f"Welcome to {__file__}!")
    read_locks = set()
    write_locks = set()

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
            lock = locks[key]
            if lock not in read_locks.union(write_locks):
                lock.acquire_write()
                write_locks.add(lock)
            db[key] = match.group(2)
        elif match := re.match(r"get (\S+)", cmd):
            key = match.group((1))
            lock = locks[key]
            if lock not in read_locks.union(write_locks):
                lock.acquire_read()
                read_locks.add(lock)
            try:
                server.send(db[key])
            except KeyError:
                # Keep the lock to prevent phantoms.
                server.send("not found")
        elif cmd == "commit":
            for lock in read_locks:
                lock.release_read()
            for lock in write_locks:
                lock.release_write()

            read_locks = set()
            write_locks = set()
        else:
            server.send("invalid syntax")

    # TODO: roll back the transaction and drop locks.
    server.close()


while True:
    sock, addr = server_socket.accept()
    threading.Thread(target=server_thread, args=(sock, addr)).start()
