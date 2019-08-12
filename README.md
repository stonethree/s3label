# README

[![Build Status](https://travis-ci.org/stonethree/s3label.svg?branch=master)](https://travis-ci.org/stonethree/s3label)

## Overview

S3Label is an open-source browser-based image labeling tool developed by [Stone Three](https://www.stonethree.com/), a company in South Africa.
The goal of S3Label is to speed up the labeling of images for use in machine learning. 
It is particularly focused on instance segmentation, semantic segmentation and keypoints, although could easily be extended to classification and other types of labeling tasks too.

![S3Label_UI](docs/visuals/label_image.png)

S3Label currently supports various types of labels:

| Label type | Description |
| ------     | ------      |
| Freehand | Click and drag a free-form polygon shape |
| Polygon | Click the individual polygon vertices |
| Rectangle | Click and drag to draw rectangular bounding boxes |
| Circle | Click and drag to draw circle |

The tool is designed to keep track of who labeled what data and to make the labeling process fast. 

Two types of user roles are available: *admin* and *normal* users:

| User role | Functionality available |
| ------    | ------      |
| Normal | Log in and label images. View own previously labeled images. |
| Admin | Same as Normal user, but also able to upload images for labeling, as well as to approve any other user's labeling. |

## Architecture

* Front-end: VueJS
* Back-end: Flask
* Database: Postgres

See [here](./docs/architecture.md) for a more thorough description and diagram of the S3Label architecture.

## Tutorials

1. [Logging in](docs/logging_in.md)
1. [Importing images for labeling](docs/upload_images.md)
1. [How to label images](./docs/how_to_label.md)
1. [Exporting labels](docs/export_labels.md)
1. [Payment tracking](./docs/making_payments.md)
1. [Useful SQL queries](./docs/useful_sql_queries.md)
1. [Roadmap](./docs/roadmap.md)

## Installation

### Back-end setup

Download and install PostgreSQL (version 9.4 or later; version 9.6 is officially tested).

Download and install [Miniconda](https://conda.io/miniconda.html). Choose Python 3 for your platform.

Switch to the back-end directory and create an environment file

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

In the back-end directory, activate the environments

~~~ bash
source activate s3label_env
~~~

Add your current path to the pythonpath variable

~~~ bash
export PYTHONPATH=$PYTHONPATH:.
~~~

Run the back-end application in development mode.

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
