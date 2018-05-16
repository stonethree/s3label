from .lib.create_app import create_app

config = {
    'username': 'postgres',
    'password': 'postgres',
    'ip': 'localhost',
    'port': 5432,
    'database_name': 's3_label_live'
}

app = create_app(config,
                 image_folder=".",
                 log_folder='/var/logs/uwsgi/app/',
                 log_file_name='s3label_python_logs.log')
