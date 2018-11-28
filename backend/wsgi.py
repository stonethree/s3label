import os

from .lib.create_app import create_app

config = {
    'username': os.environ['S3LABEL_DB_USERNAME'],
    'password': os.environ['S3LABEL_DB_PASSWORD'],
    'ip': os.environ['S3LABEL_DB_HOST'],
    'port': os.environ['S3LABEL_DB_PORT'],
    'database_name': os.environ['S3LABEL_DB_NAME'],
}

app = create_app(config,
                 image_folder=".",
                 log_folder='/var/log/uwsgi/app/',
                 log_file_name='s3label_python_logs.log')
