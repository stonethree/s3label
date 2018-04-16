-- drop previous tables

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- create tables

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
    type VARCHAR NOT NULL
        CHECK (type = 'semantic_segmentation' or type = 'instance_segmentation'),
    example_labeling VARCHAR,
	default_tool VARCHAR DEFAULT 'freehand' NOT NULL
	    CHECK (default_tool = 'freehand' or default_tool = 'polygon' or default_tool = 'select'),
	permit_overlap BOOLEAN DEFAULT false NOT NULL,
	label_classes VARCHAR DEFAULT '{"foreground_object": "(0,255,0)", "background": "(0,0,255)"}' NOT NULL);

create table input_data(
    input_data_id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    data_path VARCHAR NOT NULL);

create table users(
    user_id SERIAL PRIMARY KEY,
    user_code VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    organisation VARCHAR,
    note VARCHAR);

create table labels(
    label_id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES input_data(input_data_id) ON DELETE CASCADE,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id),
    in_progress BOOLEAN DEFAULT FALSE NOT NULL,
    user_complete BOOLEAN DEFAULT FALSE NOT NULL,
    admin_complete BOOLEAN DEFAULT NULL,
    paid BOOLEAN DEFAULT FALSE NOT NULL,
	user_comment VARCHAR,
	admin_comment VARCHAR,
	UNIQUE (input_data_id, label_task_id, user_id));
	COMMENT ON COLUMN labels.in_progress is 'User is currently labeling this item, so multiple users dont label same item';
	COMMENT ON COLUMN labels.user_complete is 'User has declared labeling of item complete';
	COMMENT ON COLUMN labels.admin_complete is 'Admin user has declared the users labeling of item complete';
	COMMENT ON COLUMN labels.paid is 'User has been paid for this label';
	COMMENT ON COLUMN labels.user_comment is 'User can communicate to admins via this field, to indicate issues with data item';
	COMMENT ON COLUMN labels.admin_comment is 'Admins can communicate to users via this field, to respond to user comments or their labeling quality';

create table label_history(
    label_history_id SERIAL PRIMARY KEY,
    label_id INTEGER REFERENCES labels(label_id) ON DELETE CASCADE,
    timestamp_edit TIMESTAMPTZ,
    label_serialised VARCHAR NOT NULL);
--    UNIQUE (label_id, timestamp_edit));
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


-- add data

INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_1', 'test_lynxx', 'This is a test. We want to segment rock images');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_2', 'test_lynxx', 'This is a test. We want to segment rock images 2');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_3', 'test_froth_sensor', 'This is a test. We want to segment rock images 3');

INSERT INTO dataset_groups(name, description) VALUES ('Lynxx datasets', 'Some description of why we grouped them...');
INSERT INTO dataset_groups(name, description) VALUES ('Subset of Lynxx datasets', 'Some description of why we grouped them...2');
INSERT INTO dataset_groups(name, description) VALUES ('Froth datasets', 'Some description of why we grouped them...3');

INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (1, 1);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (1, 2);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (2, 1);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (3, 3);

INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (1, 'Rock particle segmentation', 'Multi-instance segmentation for rock particles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (2, 'Rock particle segmentation subset', 'Multi-instance segmentation for rock particles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (3, 'Froth segmentation', 'Multi-instance segmentation for froth bubbles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (3, 'Froth segmentation 2', 'Multi-instance segmentation for froth bubbles 2', 'instance_segmentation');

INSERT INTO input_data(dataset_id, data_path) VALUES (1, 'test_images/image.jpg');
INSERT INTO input_data(dataset_id, data_path) VALUES (1, 'test_images/image2.jpg');
INSERT INTO input_data(dataset_id, data_path) VALUES (2, 'test_images/image3.jpg');
INSERT INTO input_data(dataset_id, data_path) VALUES (2, 'test_images/image4.jpg');
INSERT INTO input_data(dataset_id, data_path) VALUES (2, 'test_images/image_test.jpg');
INSERT INTO input_data(dataset_id, data_path) VALUES (3, 'test_images/froth_image.jpg');

INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('3Hx45', 'abc', 'Shaun', 'Irwin', 'shaun.irwin@stonethree.com');
INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('79ACF', 'def', 'Kristo', 'Botha', 'kristo.botha@stonethree.com');
INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('U34DA', 'ghi', 'Jimmy', 'Smith', 'test@gmail.com');
INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('E23ZG', 'jkl', 'Marcus', 'Octavius', 'test2@gmail.com');

INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) VALUES (1, 1, 1, true);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (2, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 2, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 2);
INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) VALUES (4, 1, 3, true);

INSERT INTO label_history (label_id, label_serialised) VALUES (2, '{{test: 123}}');
INSERT INTO label_history (label_id, label_serialised) VALUES (2, '{{test: 1234}}');
INSERT INTO label_history (label_id, label_serialised) VALUES (1, '{{test: 1}}');
INSERT INTO label_history (label_id, label_serialised) VALUES (3, '{{test: 4}}');
INSERT INTO label_history (label_id, label_serialised) VALUES (4, '{{test: 5}}');
INSERT INTO label_history (label_id, label_serialised) VALUES (5, '{{test: 6}}');

INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 1, 1);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 1, 5);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (3, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (4, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (5, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 2, 11);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 2, 15);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (6, 3, 23);
