import json
import unittest
from datetime import datetime

from last_searches_server import app, client


class TestMostPopularRoute(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        client.db.last_searches.drop()

    def test_most_popular_endpoint_limit_1(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()}
        ]
        client.db.last_searches.insert_many(sample_data)

        response = self.app.get('/mostPopular?limit=1')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('mostSearched', data)
        self.assertEqual(len(data['mostSearched']), 1)

    def test_most_popular_endpoint_limit_bigger_then_result(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
        ]
        client.db.last_searches.insert_many(sample_data)

        response = self.app.get('/mostPopular?limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('mostSearched', data)
        self.assertEqual(len(data['mostSearched']), 2)

    def test_most_popular_endpoint_data_with_old_data(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime(2000, 12, 12).timestamp()},
        ]
        client.db.last_searches.insert_many(sample_data)

        response = self.app.get('/mostPopular?limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('mostSearched', data)
        self.assertEqual(len(data['mostSearched']), 1)

    def test_most_popular_endpoint_sorted_by_most_hits(self):
        sample_data = [
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Flask', 'timestamp': datetime.utcnow()},
            {'userId': 'user123', 'searchPhrase': 'Python', 'timestamp': datetime.utcnow()}
        ]
        client.db.last_searches.insert_many(sample_data)

        response = self.app.get('/mostPopular?limit=2')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('mostSearched', data)
        self.assertEqual(len(data['mostSearched']), 2)
        self.assertEqual(data['mostSearched'][0]["searchPhrase"], "Python")
        self.assertEqual(data['mostSearched'][1]["searchPhrase"], "Flask")
        self.assertEqual(data['mostSearched'][0]["hits"], 2)
        self.assertEqual(data['mostSearched'][1]["hits"], 1)