-- This file lists the commands used to generate the Postgres tables
-- We might opt for SQLAlchemy or similar at a later stage

-- 1. Create the 's3_label' database

-- 2. Create the user 's3_label_admin'

create user s3_label_admin with password 's3_label_admin;';

-- 3. Create tables

create table datasets(
    id SERIAL PRIMARY KEY,
    site VARCHAR,
    sensor VARCHAR,
    description VARCHAR);

create table dataset_groups(
    id SERIAL PRIMARY KEY,
    label_task_id INTEGER REFERENCES datasets(id),
    dataset_id INTEGER);

create table label_tasks(
    id SERIAL PRIMARY KEY,
    dataset_group_id INTEGER REFERENCES dataset_groups(id),
    title VARCHAR,
    description VARCHAR,
    example_labeling VARCHAR);

create table input_data(
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    image_path VARCHAR,
    priority INTEGER);

create table users(
    id SERIAL PRIMARY KEY,
    user_code VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR);

create table labels(
    id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES datasets(id),
    label_task_id INTEGER REFERENCES label_tasks(id),
    user_id INTEGER REFERENCES users(id),
    in_progress BOOLEAN,
    verified_done BOOLEAN,
    paid BOOLEAN);

create table label_history(
    id SERIAL PRIMARY KEY,
    label_id INTEGER REFERENCES labels(id),
    timestamp_edit TIMESTAMPTZ,
    label_serialised VARCHAR);
