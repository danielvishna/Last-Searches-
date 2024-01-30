import unittest
from unittest.mock import patch

from pymongo.errors import ConnectionFailure

from last_searches_server import app


class TestHealthRoute(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_health_success(self):
        response = self.app.get('/health')

        self.assertEqual(response.status_code, 200)

    @patch('last_searches_server.client.db')
    def test_health_failure(self, mock_mongo_client_db):
        mock_mongo_client_db.command.side_effect = ConnectionFailure(message="Simulated connection error")

        expected_error_message = "Simulated connection error"

        response = self.app.get('/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, expected_error_message)
