import unittest
from unittest.mock import patch
from datetime import datetime

from last_searches_server import app


class TestLastSearchRoute(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_last_search_missing_data(self):
        response = self.client.post('/lastSearch')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(None, response.get_json())

    def test_last_search_success(self):
        mock_data = {
            'userId': 'bob',
            'searchPhrase': 'test movie',
            'timestamp': datetime.utcnow()
        }

        with patch('pymongo.collection.Collection.insert_one') as mock_insert:
            response = self.client.post('/lastSearch', json=mock_data)

            self.assertEqual(response.status_code, 201)
            inserted = mock_insert.call_args[0][0]
            self.assertIn('timestamp', inserted)
            self.assertLessEqual(inserted['timestamp'], datetime.utcnow())

    def test_last_search_failure(self):
        mock_data = {'userId': 'bob', 'searchPhrase': 'test movie'}

        with patch('pymongo.collection.Collection.insert_one') as mock_insert:
            mock_insert.side_effect = Exception('Insert error')

            response = self.client.post('/lastSearch', json=mock_data)

            self.assertEqual(response.status_code, 500)
            self.assertEqual(None, response.get_json())


if __name__ == '__main__':
    unittest.main()
