import unittest
from unittest.mock import patch
from datetime import datetime

from last_searches_server import app


class TestLastSearchAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_hello_api_reachable(self):
        response = self.client.get('/hello')
        assert response.status_code == 200

    def test_hello_response_body(self):
        response = self.client.get('/hello')
        assert response.data == b''

    def test_hello_valid_methods(self):
        response = self.client.get('/hello')
        assert response.status_code == 200

        response = self.client.post('/hello')
        assert response.status_code != 200


    def test_missing_data(self):
        response = self.client.post('/lastSearch')
        self.assertEqual(response.status_code, 400)

        json = response.get_json()
        self.assertIn('error', json)
        self.assertEqual(json['error'], 'Missing required fields')

    def test_success(self):
        mock_data = {
            'userId': 'bob',
            'searchPhrase': 'test movie',
            'timestamp': datetime.utcnow()
        }

        with patch('pymongo.collection.Collection.insert_one') as mock_insert:
            response = self.client.post('/lastSearch', json=mock_data)
            self.assertEqual(response.status_code, 201)

            # Assert timestamp was saved
            inserted = mock_insert.call_args[0][0]
            self.assertIn('timestamp', inserted)

            # Allow some variance in timestamp
            self.assertLessEqual(inserted['timestamp'], datetime.utcnow())

    def test_insert_failure(self):
        mock_data = {'userId': 'bob', 'searchPhrase': 'test movie'}

        with patch('pymongo.collection.Collection.insert_one') as mock_insert:
            mock_insert.side_effect = Exception('Insert error')

            response = self.client.post('/lastSearch', json=mock_data)
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()