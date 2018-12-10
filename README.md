# README

## Contents

1. Installation
2. [Importing Labels](./docs/import_label.md)
3. [Exporting Labels](./docs/export_label.md)
4. [Labels](./docs/label.md)
5. [Features](./docs/features.md)
6. [Payment Tracking](./docs/making_payments.md)
7.  [Useful SQL queries](./docs/useful_sql_queries.md)
8. [Troubleshooting](./docs/troubleshoot.md)

## Installation

### Backend Setup

Download and install PostgreSQL (ver. 9.4 or later; ver. 9.6 is officially tested)

Download and install [Miniconda](https://conda.io/miniconda.html) using Python 3

Switch to the backend directory and create an environmental file

~~~ bash
cd backend
conda env update
~~~

Generate a database called s3_label

~~~ bash
createdb -h <host> -p <port> -U <username> <database_name>
~~~

Run scripts to create database tables and populate it with unit test data

~~~ bash
psql -U <username> -d <database_name> -f <filename>

# SQL file to create database tables:
create_db_tables.sql

# SQL file to populate with unit test data:
init_unit_test_data.sql
~~~

In the backend directory, activate the environments

~~~ bash
source activate flask_env
~~~

Add your current path to the pythonpath variable

~~~ bash
export PYTHONPATH=$PYTHONPATH:
~~~

Run the backend with main.py

~~~ bash
python main.py <args if required>
~~~

### Front-end Setup

Install frontend dependencies

~~~ bash
cd ../frontend/spa/
npm install
~~~

Run the application. Application will then be running at http://localhost.8080

~~~ bash
npm run dev
~~~
