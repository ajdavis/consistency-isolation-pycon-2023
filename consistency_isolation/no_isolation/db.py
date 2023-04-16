from .. import Server, ServerConnection

db: dict[str, str] = {}


def server_thread(server: ServerConnection):
    while True:
        cmd = server.next_command()
        if cmd is None or cmd.name == "bye":
            break
        elif cmd.name == "set":
            db[cmd.key] = cmd.value
        elif cmd.name == "get":
            try:
                server.send(db[cmd.key])
            except KeyError:
                server.send("not found")
        elif cmd.name == "commit":
            pass
        else:
            server.send("invalid syntax")


Server().serve(server_thread)
