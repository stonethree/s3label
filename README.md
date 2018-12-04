# README

## Contents

1.  Installation
2.  [Importing Labels](./docs/import_label.md)
3.  [Exporting Labels](./docs/export_label.md)
4.  [Labels](./docs/label.md)
5.  [Features](./docs/features.md)
6.  [Troubleshooting](./docs/troubleshoot.md)

## Installation

### Backend Setup
Download and install PostgreSQL (ver. 9.4 or later; ver. 9.6 is officially tested)

Download and install [Miniconda](https://conda.io/miniconda.html) using Python 3

Switch to the backend directory and create an environmental file
~~~
cd backend
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
In the backend directory, activate the environments
~~~
source activate
~~~
Export your current path to the pythonpath variable
~~~
export PYTHONPATH=$PYTHONPATH:
~~~
Run the backend with main.py
~~~
python main.py <args if required>
~~~
### Frontend Setup
Install frontend dependencies.
~~~
cd ../frontend/spa/
npm install
~~~
Compile and run the application. Application will then be running at http://localhost.8080
~~~
npm run dev
~~~