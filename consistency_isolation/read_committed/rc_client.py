import threading

from .. import Client

lock = threading.Lock()
amount_withdrawn = 0
key = "jesse-savings"
tn = Client()
tn.send(f"set {key} 1")  # I have one dollar in the bank.
tn.send("commit")


def withdraw_1(thread_id):
    global amount_withdrawn
    local_tn = Client()
    local_tn.send(f"get {key}")
    balance = int(local_tn.readline())
    print(f"Thread {thread_id} sees balance: {balance}")
    if balance >= 1:
        balance -= 1
        local_tn.send(f"set {key} {balance}")
        local_tn.send("commit")
        print(f"Thread {thread_id} withdrew a dollar")
        with lock:
            amount_withdrawn += 1


t1 = threading.Thread(target=withdraw_1, args=[1])
t2 = threading.Thread(target=withdraw_1, args=[2])
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Amount withdrawn: {amount_withdrawn}")
tn.send(f"get {key}")
print(f"Amount on server: {tn.readline()}")
