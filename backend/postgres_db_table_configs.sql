-- This file lists the commands used to generate the Postgres tables
-- We might opt for SQLAlchemy or similar at a later stage

-- 1. Create the 's3_label' database

-- 2. Create the user 's3_label_admin'

create user s3_label_admin with password 's3_label_admin;';

-- 3. Create tables

create table datasets(
    dataset_id SERIAL PRIMARY KEY,
    site VARCHAR NOT NULL,
    sensor VARCHAR NOT NULL,
    dataset_description VARCHAR NOT NULL);

create table dataset_groups(
    group_id SERIAL PRIMARY KEY,
    group_name VARCHAR UNIQUE NOT NULL,
    group_description VARCHAR);

create table dataset_group_lists(
    group_id INTEGER REFERENCES dataset_groups(group_id),
    dataset_id INTEGER REFERENCES datasets(dataset_id),
    PRIMARY KEY (group_id, dataset_id));

create table label_tasks(
    label_task_id SERIAL PRIMARY KEY,
    dataset_group_id INTEGER REFERENCES dataset_groups(group_id),
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    example_labeling VARCHAR);

create table input_data(
    input_data_id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(dataset_id),
    image_path VARCHAR NOT NULL,
    priority INTEGER DEFAULT 1 NOT NULL);     -- TODO: need to make "priority" linked to a label task, since an image can be high priority for one task and low for another

create table users(
    user_id SERIAL PRIMARY KEY,
    user_code VARCHAR UNIQUE NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL);

create table labels(
    label_id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES input_data(input_data_id),
    label_task_id INTEGER REFERENCES label_tasks(label_task_id),
    user_id INTEGER REFERENCES users(user_id),
    in_progress BOOLEAN DEFAULT FALSE NOT NULL,
    verified BOOLEAN DEFAULT FALSE NOT NULL,
    paid BOOLEAN DEFAULT FALSE NOT NULL);

create table label_history(
    label_history_id SERIAL PRIMARY KEY,
    label_id INTEGER REFERENCES labels(label_id),
    timestamp_edit TIMESTAMPTZ,
    label_serialised VARCHAR NOT NULL,
    UNIQUE (label_id, timestamp_edit));
ALTER TABLE label_history ALTER COLUMN timestamp_edit SET DEFAULT now();
