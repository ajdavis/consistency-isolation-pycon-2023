from .. import Server, ServerConnection

db: dict[str, str] = {}


def server_thread(server: ServerConnection):
    txn = db.copy()  # Create a snapshot.
    while True:
        cmd = server.next_command()
        if cmd is None:
            break
        elif cmd.name == "bye":
            server.send("bye")
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
            db.update(txn)
            txn = db.copy()


Server().serve(server_thread)
