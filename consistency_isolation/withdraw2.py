import threading

from . import ClientConnection

lock = threading.Lock()
amount_withdrawn = 0
key = "jesse-savings"
client = ClientConnection()
client.send(f"set {key} 1")  # I have one dollar in the bank.
client.send("commit")


def withdraw_1(thread_id):
    global amount_withdrawn
    c = ClientConnection()
    c.send(f"get {key}")
    balance = int(c.readline())
    print(f"Thread {thread_id} sees balance: {balance}")
    if balance >= 1:
        balance -= 1
        c.send(f"set {key} {balance}")
        print(f"Thread {thread_id} withdrew a dollar")
        with lock:
            amount_withdrawn += 1
    else:
        print(f"Thread {thread_id} can't withdraw any money")

    c.send("commit")


t1 = threading.Thread(target=withdraw_1, args=[1])
t2 = threading.Thread(target=withdraw_1, args=[2])
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Amount withdrawn: {amount_withdrawn}")
# In snapshot isolation, we need to restart txn to see fresh data.
client = ClientConnection()
client.send(f"get {key}")
print(f"Amount on server: {client.readline()}")
client.send("commit")
