from .unit_test_utils import AuthActions

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
              'port': '5432',
              'database_name': 's3_label_test'}

    test_app = create_app(config, '.')

    yield test_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth(client):
    return AuthActions(client)
