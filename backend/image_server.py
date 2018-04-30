from flask import Flask
from flask_cors import CORS, cross_origin
import flask_jwt_extended as fje
from sqlalchemy import create_engine
import argparse

from backend.lib.endpoints import ebp


def create_app(db_config):
    # set the project root directory as the static folder, you can set others.
    app = Flask(__name__, static_url_path='')

    # https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
    # pip install -U flask-cors
    CORS(app, resources={r"/*": {"origins": "*"}})

    engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(db_config['username'],
                                                                  db_config['password'],
                                                                  db_config['ip'],
                                                                  db_config['database_name']))

    print('Current database being used: ', db_config['database_name'])

    app.config['engine'] = engine

    # Setup the Flask-JWT-Extended extension
    app.config['JWT_SECRET_KEY'] = 's3label-completely-secret'  # this should be kept secret!
    jwt = fje.JWTManager(app)

    # register the endpoints with this app
    app.register_blueprint(ebp)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backend server for the S3 Label web app')
    # parser.add_argument('--use_test_database', action='store_true', help='Use test database instead of the live one')
    args = parser.parse_args()

    # if args.use_test_database:
    #     config = {'username': 'postgres',
    #               'password': 'postgres',
    #               'ip': 'localhost',
    #               'database_name': 's3_label_test'}
    # else:
    config = {'username': 'postgres',
              'password': 'postgres',
              'ip': 'localhost',
              'database_name': 's3_label'}

    s3_label_app = create_app(config)

    s3_label_app.run(debug=True)
