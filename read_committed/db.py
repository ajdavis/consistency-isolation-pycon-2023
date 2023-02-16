import uuid

from flask import abort, Flask, request

app = Flask(__name__)
db = {}
transactions = {}


@app.route('/key/<key>', methods=['GET', 'PUT'])
def key_handler(key: str):
    if request.method == 'GET':
        try:

            return db[key]
        except KeyError:
            abort(404)
    else:
        db[key] = request.json["value"]
        return ""


@app.route('/start_txn', methods=['POST'])
def start_txn():
    txn_id = uuid.uuid4().hex
    transactions[txn_id] = {}
    return txn_id


@app.route('/commit_txn', methods=['POST'])
def commit_txn():
    return ""
