import collections
from threading import RLock

from .. import Server, ServerConnection

db: dict[str, str] = {}
locks: dict[str, RLock] = collections.defaultdict(RLock)

def server_thread(server: ServerConnection):
    txn_locks = []

    def acquire_lock(k: str):
        lock = locks[k]; lock.acquire()
        txn_locks.append(lock)

    while True:
        cmd = server.next_command()
        if cmd is None or cmd.name == "bye":
            break
        elif cmd.name == "set":
            acquire_lock(cmd.key)
            db[cmd.key] = cmd.value
        elif cmd.name == "get":
            key = cmd.key
            with locks[key]:
                try:
                    server.send(db[key])
                except KeyError:
                    server.send("not found")
        elif cmd.name == "commit":
            while txn_locks:
                txn_locks.pop().release()
        else:
            server.send("invalid syntax")


Server().serve(server_thread)
