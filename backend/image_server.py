import argparse

from backend.lib.create_app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backend server for the S3 Label web app')
    parser.add_argument('--image_folder', action='store', default='.', help='Folder path of images')
    parser.add_argument('--port', action='store', default='5433', help='Port number')
    parser.add_argument('--database_name', action='store', default='s3_label', help='Database to connect to')
    args = parser.parse_args()

    config = {'username': 'postgres',
              'password': 'postgres',
              'ip': 'localhost',
              'port': args.port,
              'database_name': args.database_name}

    print('image_folder:', args.image_folder)

    s3_label_app = create_app(config, image_folder=args.image_folder)

    s3_label_app.run(debug=True)
