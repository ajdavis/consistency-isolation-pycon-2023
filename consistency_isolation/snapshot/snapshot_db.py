import collections
import threading

from .. import Server, ServerConnection

db = {}
write_time = collections.defaultdict(int)
next_time = 1
lock = threading.Lock()  # Guards db, write_time, and next_time.

def server_thread(server: ServerConnection):
    global next_time
    with lock:
        snapshot = db.copy(); writes = {}; start = next_time; next_time += 1

    while True:
        cmd = server.next_command()
        if cmd is None or cmd.name == "bye":
            break
        elif cmd.name == "set":
            writes[cmd.key] = snapshot[cmd.key] = cmd.value  # Store writes in txn dict.
        elif cmd.name == "get":
            try:
                server.send(snapshot[cmd.key])
            except KeyError:
                server.send("not found")
        elif cmd.name == "commit":
            with lock:
                commit_time = next_time; next_time += 1
                # Another txn wrote to the same key(s) and committed.
                if any(start <= write_time[k] <= commit_time for k in writes):
                    server.send("aborted")
                else:
                    write_time.update({k: commit_time for k in writes})
                    db.update(writes)
                snapshot = db.copy(); writes = {}; start = next_time; next_time += 1


Server().serve(server_thread)
