import threading

from . import ClientConnection

lock = threading.Lock()
n_taken = 0
key = "number-of-shuttles"
client = ClientConnection()
client.send(f"set {key} 1")  # There is one shuttle in the shuttlebay.
client.send("commit")


def withdraw_1(thread_id):
    global n_taken
    c = ClientConnection()
    c.send(f"get {key}")
    n = int(c.readline())
    print(f"Thread {thread_id} sees: {n}")
    if n >= 1:
        n -= 1
        c.send(f"set {key} {n}")
        print(f"Thread {thread_id} took the shuttle")
        with lock:
            n_taken += 1
    else:
        print(f"Thread {thread_id} can't take the shuttle")

    c.send("commit")


t1 = threading.Thread(target=withdraw_1, args=[1])
t2 = threading.Thread(target=withdraw_1, args=[2])
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Number of shuttles taken: {n_taken}")
# In snapshot isolation, we need to restart txn to see fresh data.
client = ClientConnection()
client.send(f"get {key}")
print(f"Number in the shuttlebay according to the server: {client.readline()}")
client.send("commit")
