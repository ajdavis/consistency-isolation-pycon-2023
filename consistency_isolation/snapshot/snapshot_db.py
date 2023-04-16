import threading

from .. import Server, ServerConnection

db: dict[str, str] = {}
lock = threading.Lock()

def server_thread(server: ServerConnection):
    with lock:
        txn = db.copy()  # Create a snapshot.

    while True:
        cmd = server.next_command()
        if cmd is None or cmd.name == "bye":
            break
        elif cmd.name == "set":
            # Store writes in txn dict.
            txn[cmd.key] = cmd.value
        elif cmd.name == "get":
            try:
                server.send(txn[cmd.key])
            except KeyError:
                server.send("not found")
        elif cmd.name == "commit":
            with lock:
                db.update(txn)
                txn = db.copy()


Server().serve(server_thread)
