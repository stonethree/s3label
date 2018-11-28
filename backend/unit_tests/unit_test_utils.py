import psycopg2
from sqlalchemy import create_engine
import json
import pandas as pd


def connect_to_db_psycopg(config):

    conn = psycopg2.connect(host=config['ip'],
                            database=config['database_name'],
                            user=config['username'],
                            port=config['port'],
                            password=config['password'])

    return conn


def connect_to_db_sqlalchemy(config):

    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(config['username'],
                                                                config['password'],
                                                                config['ip'],
                                                                config['port'],
                                                                config['database_name']))

    return engine


def reset_db_contents(config):
    """

    :param config: Dictionary of database config parameters
    :return:
    """

    connection = connect_to_db_psycopg(config)

    connection.autocommit = True

    with connection as conn:
        with conn.cursor() as cursor:
            cursor.execute(open('unit_test_data/create_db_tables.sql', 'r').read())
            cursor.execute(open('unit_test_data/init_unit_test_data.sql', 'r').read())


def json_of_response(response):
    """ Decode json from response """
    return json.loads(response.data.decode('utf8'))


def nans_to_nones(df):
    return df.where((pd.notnull(df)), None)


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
