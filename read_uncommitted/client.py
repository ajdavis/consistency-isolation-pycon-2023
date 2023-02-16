import threading

import requests

lock = threading.Lock()
amount_withdrawn = 0

BASE_URL = "http://127.0.0.1:5000"
KEY_URL = f"{BASE_URL}/key/jesse-balance"
txn_id = requests.post(f"{BASE_URL}/start_txn").text
# I have one dollar in the bank.
requests.put(KEY_URL, json={"txn_id": txn_id, "value": "1"})
requests.post(f"{BASE_URL}/commit", json={"txn_id": txn_id})


def withdraw_1(thread_id):
    global amount_withdrawn

    txn_id = requests.post(f"{BASE_URL}/start_txn").text
    balance = int(requests.post(KEY_URL, json={"txn_id": txn_id}).text)
    print(f"Thread {thread_id} sees balance: {balance}")
    if balance >= 1:
        balance -= 1
        requests.put(KEY_URL, json={"txn_id": txn_id, "value": str(balance)})
        requests.post(f"{BASE_URL}/commit", json={"txn_id": txn_id})
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
