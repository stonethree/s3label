import argparse

from backend.lib.create_app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backend server for the S3 Label web app')
    parser.add_argument('--image_folder', action='store', default='.', help='Folder path of images')
    parser.add_argument('--username', action='store', default='postgres', help='Username for connecting to database')
    parser.add_argument('--password', action='store', default='postgres', help='Password for connecting to database')
    parser.add_argument('--host', action='store', default='localhost', help='IP address of postgres server')
    parser.add_argument('--port', action='store', default='5432', help='Port number')
    parser.add_argument('--database_name', action='store', default='s3_label', help='Database to connect to')
    parser.add_argument('--log_folder', action='store', default='/var/log', help='Folder to log to')
    parser.add_argument('--log_file_name', action='store', default='flask.log', help='File name of log file')
    args = parser.parse_args()

    config = {'username': args.username,
              'password': args.password,
              'ip': args.host,
              'port': args.port,
              'database_name': args.database_name}

    s3_label_app = create_app(config,
                              image_folder=args.image_folder,
                              log_folder=args.log_folder,
                              log_file_name=args.log_file_name)

    s3_label_app.run(host='0.0.0.0',port=5000,debug=True)
