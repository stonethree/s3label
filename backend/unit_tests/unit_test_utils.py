import psycopg2
from sqlalchemy import create_engine
import json
import pandas as pd


def get_db_config():
    return {'username': 'postgres',
            'password': 'postgres',
            'ip': 'localhost',
            'database_name': 's3_label_test'}


def connect_to_db_psycopg():
    config = get_db_config()
    conn = psycopg2.connect(host=config['ip'],
                            database=config['database_name'],
                            user=config['username'],
                            password=config['password'])

    return conn


def connect_to_db_sqlalchemy():
    config = get_db_config()
    engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(config['username'],
                                                                  config['password'],
                                                                  config['ip'],
                                                                  config['database_name']))

    return engine


def reset_db_contents():
    connection = connect_to_db_psycopg()

    connection.autocommit = True

    with connection as conn:
        with conn.cursor() as cursor:
            cursor.execute(open('unit_test_data/setup_test_db.sql', 'r').read())


def json_of_response(response):
    """ Decode json from response """
    return json.loads(response.data.decode('utf8'))


def nans_to_nones(df):
    return df.where((pd.notnull(df)), None)
