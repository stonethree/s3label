import argparse

from backend.lib.create_app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backend server for the S3 Label web app')
    # parser.add_argument('--use_test_database', action='store_true', help='Use test database instead of the live one')
    args = parser.parse_args()

    config = {'username': 'postgres',
              'password': 'postgres',
              'ip': 'localhost',
              'database_name': 's3_label'}

    s3_label_app = create_app(config)

    s3_label_app.run(debug=True)
