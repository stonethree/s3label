import argparse

from backend.lib.create_app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backend server for the S3 Label web app')
    parser.add_argument('--image_folder', action='store', default='.', help='Folder path of images')
    args = parser.parse_args()

    config = {'username': 'postgres',
              'password': 'postgres',
              'ip': 'localhost',
              'database_name': 's3_label'}

    print('image_folder:', args.image_folder)

    s3_label_app = create_app(config, image_folder=args.image_folder)

    s3_label_app.run(debug=True)
