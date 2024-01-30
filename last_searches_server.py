from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['last_searches']
searches_collection = db['searches']
# Temporary page that help me see if the server work.
@app.route('/')
def home():
    return "<h1>hello</h1>"

# API 1: Hello
@app.route('/hello', methods=['GET'])
def hello():
    return '', 200

# API 2: Set a search phrase to a user
@app.route('/lastSearch', methods=['POST'])
def last_search():

    data = request.get_json(silent=True)
    if data is None or not all(key in data for key in ('userId', 'searchPhrase')):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        client.db.last_searches.insert_one({
            'userId': data['userId'],
            'searchPhrase': data['searchPhrase'],
            'timestamp': datetime.utcnow()
        })
        return jsonify({}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True ,port=8080)
    # client.close()