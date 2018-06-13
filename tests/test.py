import json

# import your app module
import api.api

from tornado.testing import AsyncHTTPTestCase

# Create your Application for testing
app = api.api.Application()


class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return app


class TestApiHandler(TestHandlerBase):

    def test_get(self):
        response = self.fetch(
            '/v1',
            method='GET')

        entries = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEquals(response.headers['Content-Type'],
                          'application/json; charset="utf-8"')
        self.assertIsInstance(entries, dict)


class TestHealthzHandler(TestHandlerBase):

    def test_get(self):
        response = self.fetch(
            '/healthz',
            method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'')
