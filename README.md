# README

## Contents

1.  Installation
2.  [Importing Labels](./docs/import_label.md)
3.  [Exporting Labels](./docs/export_label.md)
4.  [Labels]()
5.  [Features](./docs/features.md)
6.  [Troubleshooting](./docs/troubleshoot.md)

## Installation

### Backend Setup
Download and install PostgreSQL (ver. 10 or later)

Download and install [Miniconda](https://conda.io/miniconda.html) using Python 3.7 (dependencies)

Using Anaconda Prompt, switch to the backend directory and create an environmental file
~~~
cd <PATH>
conda env update
~~~
Generate a database called s3_label
~~~
createdb -h <host> -p <port> -U <username> <database_name>
~~~
Run scripts to create database tables and populate it with unit test data
~~~
psql -U <username> -d <database_name> -f <filename>

SQL file to create database tables:
create_db_tables.sql

SQL file to populate with unit test data:
init_unit_test_data.sql
~~~
In IDE, create a new Python run configuration called main and then run main configuration. Ensure the following paths and settings are correct:
~~~
script path: <PATH to main.py in backend directory>
Python interpreter: Python 3.5 (s3_label)
working directory: <PATH to backend directory>
~~~
### Frontend Setup
From spa folder of the frontend directory, install dependencies.
~~~
cd <PATH>
npm install
~~~
Compile and run the application. Application will then be running at http://localhost.8080
~~~
npm run dev
~~~