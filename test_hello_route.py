import unittest

from last_searches_server import app


class TestLastSearchRoute(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_hello_success(self):
        response = self.client.get('/hello')
        assert response.status_code == 200
        assert response.text == ''

    def test_hello_invalid_methods(self):
        response = self.client.post('/hello')
        assert response.status_code != 200
