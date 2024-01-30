import requests
from last_searches_server import db
from pymongo.errors import ServerSelectionTimeoutError
from unittest.mock import patch
from last_searches_server import app




def get_saved_searches(user_id):
    searches = db.last_searches.find({'userId': user_id})
    return [s['searchPhrase'] for s in searches]
def test_last_search_api(client):
    # Test missing data
    response = client.post('http://localhost:8080/lastSearch')
    assert response.status_code == 400

    # # Test success
    data = {'userId': 'bob', 'searchPhrase': 'test movie'}
    response = client.post('http://localhost:8080/lastSearch', json=data)
    assert response.status_code == 201

    # Verify data inserted in DB
    assert 'test movie' in get_saved_searches('bob')

    # # Test insert failure
    # with patch('pymongo.MongoClient') as mock_client:
    #     mock_client.return_value.last_searches.insert_one.side_effect = ServerSelectionTimeoutError
    #
    #     response = client.post('http://localhost:8080/lastSearch', json=data)
    #     print(response)
    #     assert response.status_code == 500

if __name__ == '__main__':
    app.config['TESTING'] = True
    client = app.test_client()
    test_last_search_api(client)