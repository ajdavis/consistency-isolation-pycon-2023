import threading

from .. import Server, ServerConnection

db: dict[str, str] = {}
lock = threading.Lock()

def server_thread(server: ServerConnection):
    with lock:
        snapshot = db.copy(); writes = {}

    while True:
        cmd = server.next_command()
        if cmd is None or cmd.name == "bye":
            break
        elif cmd.name == "set":
            # Store writes in txn dict.
            writes[cmd.key] = snapshot[cmd.key] = cmd.value
        elif cmd.name == "get":
            try:
                server.send(snapshot[cmd.key])
            except KeyError:
                server.send("not found")
        elif cmd.name == "commit":
            with lock:
                db.update(writes)
                snapshot = db.copy(); writes = {}


Server().serve(server_thread)
