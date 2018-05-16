from flask import Flask
from flask_cors import CORS, cross_origin
import flask_jwt_extended as fje
from sqlalchemy import create_engine
from logging.handlers import RotatingFileHandler
import logging
import os

from backend.lib.endpoints import ebp


def create_app(db_config, image_folder, log_folder=None, log_file_name=None):
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

    app.config['engine'] = engine
    app.config['image_folder'] = image_folder

    if log_folder is not None and log_file_name is not None:
        configure_logging(log_folder, log_file_name)

    logger = logging.getLogger(__name__)
    logger.info('Current database being used: {}'.format(db_config['database_name']))
    logger.info('image_folder: {}'.format(app.config['image_folder']))

    # Setup the Flask-JWT-Extended extension
    app.config['JWT_SECRET_KEY'] = 's3label-completely-secret'  # this should be kept secret!
    jwt = fje.JWTManager(app)

    # register the endpoints with this app
    app.register_blueprint(ebp)

    return app


def configure_logging(log_folder, log_file_name):
    # set format of log messages

    formatter = logging.Formatter('%(asctime)s [ %(levelname)s ] [ %(filename)s : '
                                  '%(lineno)d ] [ %(threadName)s ] %(message)s')
    logging.basicConfig(level=logging.DEBUG)

    # remove default stream logger

    logger = logging.getLogger()
    h_default = logger.handlers[0]
    logger.removeHandler(h_default)

    # format stream logger (i.e. the messages logged to the console)

    h1 = logging.StreamHandler()
    h1.setFormatter(formatter)

    if log_folder is not None and log_file_name is not None:
        # create log folder if it does not yet exist

        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # also log to disk with log rotations to prevent file size becoming too large

        h = RotatingFileHandler(filename=os.path.join(log_folder, log_file_name),
                                maxBytes=int(20 * 1e6),
                                backupCount=5)
        h.setFormatter(formatter)

        logging.getLogger().addHandler(h)
        logging.getLogger().addHandler(h1)

