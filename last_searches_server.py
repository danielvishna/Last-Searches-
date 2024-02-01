from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['last_searches']
searches_collection = db['searches']


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
        if len(data) != 2:
            raise ValueError("only userId and search_phrase must be supplied")

        if not user_id:
            raise ValueError("userId must be supplied")

        if not search_phrase:
            raise ValueError("searchPhrase must be supplied")

        timestamp = datetime.utcnow()
        search_phrase = search_phrase.lower()
    except:
        return "", 400
    try:
        searches_collection.insert_one(
            {
                'userId': user_id,
                'searchPhrase': search_phrase,
                'timestamp': timestamp
            }
        )  # do we need to protect from sql injection?
        return "", 201
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
        if len(request.args) != 2:
            raise ValueError("only userId and limit must be supplied")
        user_id = request.args.get('userId')
        limit = request.args.get('limit')
        if not user_id:
            raise ValueError("userId must be supplied")

        if not limit or not limit.isdigit():
            raise ValueError("limit must be supplied as integer")
        limit = int(limit)
    except:
        return "", 400

    try:
        searches = list(
            searches_collection.find(
                {
                    'userId': user_id,
                    'timestamp': {'$gt': datetime.utcnow() - timedelta(weeks=2)}
                }
            ).sort('timestamp', -1)
            .limit(limit)
        )

        last_searches = [search['searchPhrase'] for search in searches]
        return jsonify({'lastSearches': last_searches}), 200
    except Exception as e:
        print(e)
        return '', 500


# API 5: Get the most popular search and number of hits for that search
@app.route('/mostPopular', methods=['GET'])
def get_most_popular():
    try:
        if len(request.args) != 1:
            raise ValueError("only limit must be supplied")
        limit = request.args.get('limit')
        if not limit or not limit.isdigit():
            raise ValueError("limit must be supplied as integer")
        limit = int(limit)
    except:
        return "", 400
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    try:
        result = list(searches_collection.aggregate([
            {'$match': {'timestamp': {'$gte': start_date}}},
            {'$group': {'_id': '$searchPhrase', 'hits': {'$sum': 1}}},
            {'$sort': {'hits': -1}},
            {'$limit': limit}
        ]))

        most_searched = [{'searchPhrase': r['_id'], 'hits': r['hits']} for r in result]
        return jsonify({'mostSearched': most_searched}), 200
    except Exception as e:
        print(e)
        return '', 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
    client.close()
