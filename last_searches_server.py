from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')


# API 1: Hello
@app.route('/hello', methods=['GET'])
def hello():
    return '', 200


# API 2: Set a search phrase to a user
@app.route('/lastSearch', methods=['POST'])
def last_search():
    try:
        data = request.get_json(silent=True)
        user_id = data.get('userId')
        search_phrase = data.get('searchPhrase')

        if not user_id:
            raise ValueError("userId must be supplied")

        if not search_phrase:
            raise ValueError("searchPhrase must be supplied")

        timestamp = datetime.utcnow()
    except:
        return "", 400
    try:
        client.db.last_searches.insert_one({
            'userId': user_id,
            'searchPhrase': search_phrase,
            'timestamp': timestamp})
        return '', 201
    except:
        return "", 500


# API 3: Health
@app.route('/health', methods=['GET'])
def health():
    try:
        client.db.command("ping")
        return '', 200
    except Exception as e:
        return str(e), 500


# API 4: Get the last N searches for user X
@app.route('/lastSearches', methods=['GET'])
def get_last_searches():
    try:
        user_id = request.args.get('userId')
        limit = request.args.get('limit')
        if not user_id:
            raise ValueError("userId must be supplied")

        if not limit:
            raise ValueError("limit must be supplied")
        limit = int(limit)
    except:
        return "", 400

    try:
        searches = list(client.db.last_searches.find({
            'userId': user_id,
            'timestamp': {'$gt': datetime.utcnow() - timedelta(weeks=2)}
        }).sort('timestamp', -1).limit(limit))

        last_searches = [search['searchPhrase'] for search in searches]
        return jsonify({'lastSearches': last_searches}), 200
    except Exception as e:
        print(e)
        return '', 500




if __name__ == "__main__":
    app.run(debug=True, port=8080)
    client.close()
