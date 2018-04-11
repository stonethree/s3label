-- This file lists the commands used to generate the Postgres tables
-- We might opt for SQLAlchemy or similar at a later stage

-- 1. Create the 's3_label' database

-- 2. Create the user 's3_label_admin'

--create user s3_label_admin with password 's3_label_admin;';

-- 3. Drop existing tables

--DROP SCHEMA public CASCADE;
--CREATE SCHEMA public;

-- 4. Create tables

create table datasets(
    dataset_id SERIAL PRIMARY KEY,
    site VARCHAR NOT NULL,
    sensor VARCHAR NOT NULL,
    dataset_description VARCHAR NOT NULL);

create table dataset_groups(
    dataset_group_id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR);

create table dataset_group_lists(
    dataset_group_id INTEGER REFERENCES dataset_groups(dataset_group_id) ON DELETE CASCADE,
    dataset_id INTEGER REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    PRIMARY KEY (dataset_group_id, dataset_id));

create table label_tasks(
    label_task_id SERIAL PRIMARY KEY,
    dataset_group_id INTEGER REFERENCES dataset_groups(dataset_group_id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    example_labeling VARCHAR);

create table input_data(
    input_data_id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    image_path VARCHAR NOT NULL);

create table users(
    user_id SERIAL PRIMARY KEY,
    user_code VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL);

create table labels(
    label_id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES input_data(input_data_id) ON DELETE CASCADE,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id),
    in_progress BOOLEAN DEFAULT FALSE NOT NULL,
    verified BOOLEAN DEFAULT FALSE NOT NULL,
    paid BOOLEAN DEFAULT FALSE NOT NULL);

create table label_history(
    label_history_id SERIAL PRIMARY KEY,
    label_id INTEGER REFERENCES labels(label_id) ON DELETE CASCADE,
    timestamp_edit TIMESTAMPTZ,
    label_serialised VARCHAR NOT NULL,
    UNIQUE (label_id, timestamp_edit));
ALTER TABLE label_history ALTER COLUMN timestamp_edit SET DEFAULT now();

create table priorities(
    priority_id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES input_data(input_data_id) ON DELETE CASCADE,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1 NOT NULL);


-- views

-- show label tasks associated with each input data item
create view input_data_per_label_task as
select * from
(
	select tmp_2.*, priority from
	(
	    select input_data_id, dataset_id, dataset_group_id, label_task_id from
	    (
	        select dataset_id, input_data_id, dataset_group_id from input_data
	        inner join dataset_group_lists using (dataset_id)
	    ) as tmp
	    inner join label_tasks using (dataset_group_id)
	) as tmp_2
	inner join priorities using (input_data_id, label_task_id)
) as tmp_3
left outer join labels using (input_data_id, label_task_id);

-- show most recent label history for each label
create view latest_label_history as
select distinct on (label_id) * from
(
	select * from labels
	left outer join label_history using (label_id)
) as tmp
order by label_id, timestamp_edit desc;

-- combine most recent label history with input data info
create view latest_label_history_per_input_item as
select i.*, llh.label_history_id, llh.timestamp_edit, llh.label_serialised  from input_data_per_label_task i
left outer join latest_label_history llh using (input_data_id, label_task_id, label_id, user_id);
