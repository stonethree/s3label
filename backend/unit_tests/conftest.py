import os
import json
from .unit_test_utils import json_of_response

from backend.unit_tests import unit_test_utils
from backend.lib.create_app import create_app

import pytest


@pytest.fixture(scope="module")
def db_connection_sqlalchemy():
    return unit_test_utils.connect_to_db_sqlalchemy()


@pytest.fixture(scope="module")
def refresh_db_once():
    unit_test_utils.reset_db_contents()
    print('refreshed db contents')


@pytest.fixture()
def refresh_db_every_time():
    unit_test_utils.reset_db_contents()
    print('refreshed db contents')


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""

    config = {'username': 'postgres',
              'password': 'postgres',
              'ip': 'localhost',
              'port': '5433',
              'database_name': 's3_label_test'}

    test_app = create_app(config, '.')

    yield test_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


class AuthActions(object):
    def __init__(self, client):
        self.client = client
        self.base_url = 'http://127.0.0.1:5000/image_labeler/api/v1.0'
        self.access_token = None

    def login(self, email='test@gmail.com', password='ghi'):
        rv = self.client.post(self.base_url + '/login',
                              data=json.dumps({'email': email, 'password': password}),
                              content_type='application/json')

        # store JSON web token that we receive from the server

        resp_json = json_of_response(rv)
        self.access_token = resp_json['access_token']

        return rv

    def logout(self):
        # the server does not keep track of sessions. To logout, just delete the access token
        self.access_token = None

    def auth_header(self):
        return {'Authorization': 'Bearer ' + self.access_token}


@pytest.fixture
def auth(client):
    return AuthActions(client)
