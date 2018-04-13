from backend.unit_tests import unit_test_utils

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
