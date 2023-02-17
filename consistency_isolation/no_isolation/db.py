import re
import socket
import telnetlib
import threading


from .. import Server

db = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 23), )
server_socket.listen(1)


def server_thread(sock: socket.socket, client_addr: tuple[str, int]):
    print(f"{client_addr} connected")
    server = Server(sock)
    server.write(f"Welcome to {__file__}!")
    while True:
        try:
            data = server.readline()
        except (EOFError, ConnectionResetError):
            break  # Disconnected.

        if data == "bye":
            server.write("bye")
            break
        elif match := re.match(r"set (\S+) (\S+)", data):
            db[match.group(1)] = match.group(2)
        elif match := re.match(r"get (\S+)", data):
            try:
                server.write(db[match.group(1)])
            except KeyError:
                server.write("not found")
        else:
            server.write("invalid syntax")

    server.close()


while True:
    sock, addr = server_socket.accept()
    threading.Thread(target=server_thread, args=(sock, addr)).start()
