from flask import Flask
from flask_cors import CORS, cross_origin
import flask_jwt_extended as fje
from sqlalchemy import create_engine

from backend.lib.endpoints import ebp


def create_app(db_config, image_folder):
    # set the project root directory as the static folder, you can set others.
    app = Flask(__name__, static_url_path='')

    # https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
    # pip install -U flask-cors
    CORS(app, resources={r"/*": {"origins": "*"}})

    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(db_config['username'],
                                                                db_config['password'],
                                                                db_config['ip'],
                                                                db_config['port'],
                                                                db_config['database_name']))

    print('Current database being used: ', db_config['database_name'])

    app.config['engine'] = engine
    app.config['image_folder'] = image_folder

    # Setup the Flask-JWT-Extended extension
    app.config['JWT_SECRET_KEY'] = 's3label-completely-secret'  # this should be kept secret!
    jwt = fje.JWTManager(app)

    # register the endpoints with this app
    app.register_blueprint(ebp)

    return app
