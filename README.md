# README

[![Build Status](https://travis-ci.org/stonethree/s3label.svg?branch=master)](https://travis-ci.org/stonethree/s3label)

## Contents

1. [Installation](README.md)
2. [Importing Labels](./docs/import_label.md)
3. [Exporting Labels](./docs/export_label.md)
4. [Labels](./docs/label.md)
5. [Features](./docs/features.md)
6. [Payment Tracking](./docs/making_payments.md)
7. [Useful SQL queries](./docs/useful_sql_queries.md)
8. [Troubleshooting](./docs/troubleshoot.md)

## Installation

### Backend setup

Download and install PostgreSQL (version 9.4 or later; version 9.6 is officially tested).

Download and install [Miniconda](https://conda.io/miniconda.html). Choose Python 3 for your platform.

Switch to the backend directory and create an environment file

~~~ bash
cd backend
conda env update
~~~

Create the database (e.g. named s3_label_test)

~~~ bash
createdb -h <host> -p <port> -U <username> <database_name>
~~~

Run scripts to create database tables and populate them with unit test data

~~~ bash
# Create database tables:
psql -U <username> -d <database_name> -f create_db_tables.sql

# Populate database tables with unit test or example data:
psql -U <username> -d <database_name> -f init_unit_test_data.sql
~~~

In the backend directory, activate the environments

~~~ bash
source activate s3label_env
~~~

Add your current path to the pythonpath variable

~~~ bash
export PYTHONPATH=$PYTHONPATH:.
~~~

Run the backend application in development mode.

~~~ bash
python main.py --image_folder <path to folder containing data> 
               --username <username for database> 
               --password <password for database>
               --host <IP address of database>
               --port <port number of database>
               --database_name <database to connect to>
               --log_folder <folder to log to>
               --log_file_name <file name of log file>
~~~

If you would like to run this in production, use Gunicorn, uWSGI or other production-grade server.

#### Running unit tests

Run the unit tests using the specified database connection settings:

~~~ bash
pytest -vs --username <username> --password <password> --ip <IP address> --port <port> --databasename <database_name> unit_tests
~~~

### Front-end Setup

Install frontend dependencies

~~~ bash
cd ../frontend/spa/
npm install
~~~

Run the application in development mode. Application will then be running at http://localhost.8080.

~~~ bash
npm run dev
~~~

If you would like to run this in production, use Nginx or another production-grade server and build the dependencies as follows:

~~~ bash
npm run build
~~~
