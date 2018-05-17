from .unit_test_utils import AuthActions

from backend.unit_tests import unit_test_utils
from backend.lib.create_app import create_app

import pytest


def pytest_addoption(parser):
    """
    Adds a custom command line argument for running pytest
    """

    parser.addoption('--username', action='store', default='postgres', help='Username for database')
    parser.addoption('--password', action='store', default='postgres', help='Password for database')
    parser.addoption('--ip', action='store', default='localhost', help='Folder path of images')
    parser.addoption('--port', action='store', default='5432', help='Port number')
    parser.addoption('--database_name', action='store', default='s3_label_test', help='Database to connect to')


@pytest.fixture(scope="module")
def db_config(request):
    config = {
        'username': request.config.getoption("--username"),
        'password': request.config.getoption("--password"),
        'ip': request.config.getoption("--ip"),
        'port': request.config.getoption("--port"),
        'database_name': request.config.getoption("--database_name")
    }

    return config


@pytest.fixture(scope="module")
def db_connection_sqlalchemy(db_config):
    return unit_test_utils.connect_to_db_sqlalchemy(db_config)


@pytest.fixture(scope="module")
def refresh_db_once(db_config):
    unit_test_utils.reset_db_contents(db_config)
    print('refreshed db contents')


@pytest.fixture()
def refresh_db_every_time(db_config):
    unit_test_utils.reset_db_contents(db_config)
    print('refreshed db contents')


@pytest.fixture
def app(db_config):
    """Create and configure a new app instance for each test."""

    test_app = create_app(db_config, '.')

    yield test_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth(client):
    return AuthActions(client)
