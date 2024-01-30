import json
import unittest
from datetime import datetime, timedelta

from last_searches_server import app, searches_collection


class TestLastSearchesRoute(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        searches_collection.drop()

    def test_last_searches_endpoint_limit_1(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
        ]
        searches_collection.insert_many(sample_data)
        response = self.app.get('/lastSearches?userId=user123&limit=1')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('lastSearches', data)
        self.assertEqual(len(data['lastSearches']), 1)

    def test_last_search_not_positive_int(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
        ]
        searches_collection.insert_many(sample_data)
        response = self.app.get('/lastSearches?userId=user123&limit=-1')
        self.assertEqual(response.status_code, 400)
        response = self.app.get('/lastSearches?userId=user123&limit=0.5')
        self.assertEqual(response.status_code, 400)
        response = self.app.get('/lastSearches?userId=user123&limit=-0.5')
        self.assertEqual(response.status_code, 400)


    def test_last_searches_endpoint_limit_bigger_then_result(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
        ]
        searches_collection.insert_many(sample_data)

        response = self.app.get('/lastSearches?userId=user123&limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('lastSearches', data)
        self.assertEqual(len(data['lastSearches']), 2)

    def test_last_searches_endpoint_newer_before(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Java', 'timestamp': datetime.utcnow() - timedelta(days=2)},
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow() - timedelta(days=1)},
        ]
        searches_collection.insert_many(sample_data)

        response = self.app.get('/lastSearches?userId=user123&limit=4')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('lastSearches', data)
        self.assertEqual(len(data['lastSearches']), 3)
        self.assertEqual(data['lastSearches'][0], "Python")
        self.assertEqual(data['lastSearches'][1], "Flask")
        self.assertEqual(data['lastSearches'][2], "Java")

    def test_last_searches_endpoint_data_with_old_data(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime(2000, 12, 12).timestamp()},
        ]
        searches_collection.insert_many(sample_data)

        response = self.app.get('/lastSearches?userId=user123&limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('lastSearches', data)
        self.assertEqual(len(data['lastSearches']), 1)
        self.assertEqual(data['lastSearches'][0], "Python")

    def test_last_searches_endpoint_many_users(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user987', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
        ]
        searches_collection.insert_many(sample_data)

        response = self.app.get('/lastSearches?userId=user123&limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('lastSearches', data)
        self.assertEqual(len(data['lastSearches']), 1)
        self.assertEqual(data['lastSearches'][0], "Python")
