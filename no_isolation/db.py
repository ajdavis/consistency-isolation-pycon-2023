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
        db[key] = request.get_data()
        return ""
