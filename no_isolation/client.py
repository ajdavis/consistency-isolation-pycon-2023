import threading

import requests

lock = threading.Lock()
amount_withdrawn = 0

KEY_URL = "http://127.0.0.1:5000/key/jesse-balance"
requests.put(KEY_URL, data=str(1))  # I have one dollar in the bank.


def withdraw_1(thread_id):
    global amount_withdrawn

    balance = int(requests.get(KEY_URL).text)
    print(f"Thread {thread_id} sees balance: {balance}")
    if balance >= 1:
        balance -= 1
        requests.put(KEY_URL, str(balance))
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
print(f"Amount on server: {requests.get(KEY_URL).text}")
