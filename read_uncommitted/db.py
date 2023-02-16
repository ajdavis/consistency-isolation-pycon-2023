import uuid

from flask import abort, Flask, request

app = Flask(__name__)
db = {}


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
    return uuid.uuid4().hex


@app.route('/commit_txn', methods=['POST'])
def commit_txn():
    return ""
