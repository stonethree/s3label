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
	default_tool VARCHAR DEFAULT 'freehand' NOT NULL
	    CHECK (default_tool = 'freehand' or default_tool = 'polygon' or default_tool = 'select'),
	permit_overlap BOOLEAN DEFAULT false NOT NULL,
	label_classes VARCHAR DEFAULT '[{"label_class": "foreground_object", "color": "[0,255,0]"}, {"label_class": "background", "color": "[0,0,255]"}]' NOT NULL);

create table example_labeling(
    example_labeling_id SERIAL PRIMARY KEY,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    image_path VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL);

create table input_data(
    input_data_id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    data_path VARCHAR NOT NULL,
    sha1_hash VARCHAR NOT NULL);
    COMMENT ON COLUMN input_data.sha1_hash is 'SHA-1 hash of the file content. Useful for checking files are unique in database and for checking file identity when they are moved to other drives or folders in the future.';

create table users(
    user_id SERIAL PRIMARY KEY,
    password VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    organisation VARCHAR,
    note VARCHAR,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL);

create table users_label_tasks(
    user_label_task_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE);

create table labels(
    label_id SERIAL PRIMARY KEY,
    input_data_id INTEGER REFERENCES input_data(input_data_id) ON DELETE CASCADE,
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id),
    in_progress BOOLEAN DEFAULT FALSE NOT NULL,
    user_complete BOOLEAN DEFAULT FALSE NOT NULL,
    needs_improvement BOOLEAN DEFAULT FALSE NOT NULL,
    admin_complete BOOLEAN DEFAULT FALSE NOT NULL,
    paid BOOLEAN DEFAULT FALSE NOT NULL,
	user_comment VARCHAR,
	admin_comment VARCHAR,
	UNIQUE (input_data_id, label_task_id, user_id));
	COMMENT ON COLUMN labels.in_progress is 'User is currently labeling this item, so multiple users dont label same item';
	COMMENT ON COLUMN labels.user_complete is 'User has declared labeling of item complete';
	COMMENT ON COLUMN labels.needs_improvement is 'Admin user has declared labeling of item needs more work';
	COMMENT ON COLUMN labels.admin_complete is 'Admin user has declared the users labeling of item complete';
	COMMENT ON COLUMN labels.paid is 'User has been paid for this label';
	COMMENT ON COLUMN labels.user_comment is 'User can communicate to admins via this field, to indicate issues with data item';
	COMMENT ON COLUMN labels.admin_comment is 'Admins can communicate to users via this field, to respond to user comments or their labeling quality';

create table label_history(
    label_history_id SERIAL PRIMARY KEY,
    label_id INTEGER REFERENCES labels(label_id) ON DELETE CASCADE,
    timestamp_edit TIMESTAMPTZ,
    label_serialised JSONB NOT NULL);
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
select tmp_2.*, priority from
(
    select tmp.*, label_task_id from
    (
        select dataset_id, input_data_id, dataset_group_id from input_data
        full outer join dataset_group_lists using (dataset_id)
    ) as tmp
    full outer join label_tasks using (dataset_group_id)
) as tmp_2
full outer join priorities using (input_data_id, label_task_id)
order by label_task_id, input_data_id;

-- show label IDs and priorities associated with each input data item
create view labels_per_input_data_item as
select * from
(
    select * from input_data_per_label_task
) as tmp
full outer join labels using (input_data_id, label_task_id);

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
with t as (
    select * from
    (
        select tmp_3.*, user_id from
        (
            select * from input_data_per_label_task
        ) as tmp_3
        full outer join users_label_tasks using (label_task_id)
    ) as tmp_4
    full outer join latest_label_history using (input_data_id, label_task_id, user_id)
)
-- identify labeled and unlabeled input data items
select *, (not in_progress or in_progress isnull) and label_serialised isnull and label_id isnull as unlabeled from t;

-- count number of labeled, unlabeled and in progress items per user and label task
create view item_counts as
select user_id, label_task_id,
    count(*) as total_items,
    sum(case when unlabeled = true then 1 else 0 end) as num_unlabeled,
    sum(case when unlabeled = false then 1 else 0 end) as num_labeled,
    sum(case when in_progress = false and unlabeled = true then 1 else 0 end) as in_progress_unlabeled,
    sum(case when in_progress = false and unlabeled = false then 1 else 0 end) as in_progress_labeled,
    sum(case when user_complete = true then 1 else 0 end) as num_user_complete,
    sum(case when needs_improvement = true then 1 else 0 end) as num_needs_improvement,
    sum(case when admin_complete = true then 1 else 0 end) as num_admin_complete,
    sum(case when paid = true then 1 else 0 end) as num_paid
from latest_label_history_per_input_item
group by user_id, label_task_id;

-- add data

INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_1', 'test_lynxx', 'This is a test. We want to segment rock images');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_2', 'test_lynxx', 'This is a test. We want to segment rock images 2');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_3', 'test_froth_sensor', 'This is a test. We want to segment rock images 3');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_4', 'test_froth_sensor', 'This is a test. We want to segment rock images 3');

INSERT INTO dataset_groups(name, description) VALUES ('Lynxx datasets', 'Some description of why we grouped them...');
INSERT INTO dataset_groups(name, description) VALUES ('Subset of Lynxx datasets', 'Some description of why we grouped them...2');
INSERT INTO dataset_groups(name, description) VALUES ('Froth datasets', 'Some description of why we grouped them...3');
INSERT INTO dataset_groups(name, description) VALUES ('Group with empty dataset', 'Some description of why we grouped them...4');

INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (1, 1);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (1, 2);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (2, 1);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (3, 3);
INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (4, 4);

INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (1, 'Rock particle segmentation', 'Multi-instance segmentation for rock particles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (2, 'Rock particle segmentation subset', 'Multi-instance segmentation for rock particles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (3, 'Froth segmentation', 'Multi-instance segmentation for froth bubbles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (3, 'Froth segmentation 2', 'Multi-instance segmentation for froth bubbles 2', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (1, 'Rock particle segmentation: Initially unlabeled', 'Multi-instance segmentation for rock particles', 'instance_segmentation');
INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (4, 'No images associated', 'Multi-instance segmentation for rock particles', 'instance_segmentation');

INSERT INTO example_labeling(label_task_id, image_path, title, description) VALUES (1, 'unit_test_data/example_labelings/example_1.jpg', 'Example of good labeling', 'Here you can see a well labeled image');
INSERT INTO example_labeling(label_task_id, image_path, title, description) VALUES (1, 'unit_test_data/example_labelings/example_2.jpg', 'Example of bad labeling', 'Here you can see a <em>badly</em> labeled image');
INSERT INTO example_labeling(label_task_id, image_path, title, description) VALUES (2, 'unit_test_data/example_labelings/example_1.jpg', 'Example of good labeling', 'Here you can see a well labeled image');

INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (1, 'test_images/image.jpg', 'abc1');
INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (1, 'test_images/image2.jpg', 'abc2');
INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (2, 'test_images/image3.jpg', 'abc3');
INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (2, 'test_images/image4.jpg', 'abc4');
INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (2, 'test_images/image_test.jpg', 'abc5');
INSERT INTO input_data(dataset_id, data_path, sha1_hash) VALUES (3, 'test_images/froth_image.jpg', 'abc6');

INSERT INTO users (password, first_name, last_name, email, is_admin) VALUES ('abc', 'Shaun', 'Irwin', 'shaun.irwin@stonethree.com', true);
INSERT INTO users (password, first_name, last_name, email, is_admin) VALUES ('def', 'Kristo', 'Botha', 'kristo.botha@stonethree.com', true);
INSERT INTO users (password, first_name, last_name, email, is_admin) VALUES ('ghi', 'Jimmy', 'Smith', 'test@gmail.com', false);
INSERT INTO users (password, first_name, last_name, email, is_admin) VALUES ('jkl', 'Marcus', 'Octavius', 'test2@gmail.com', false);

INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (1, 1);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (1, 2);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (1, 3);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (1, 5);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (2, 1);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (2, 2);
INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (2, 5);

INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) VALUES (1, 1, 1, true);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (2, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 2, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 2);
INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress, user_complete, admin_complete) VALUES (4, 1, 3, true, true, true);

INSERT INTO label_history (label_id, label_serialised) VALUES (2, '[{"test": 123}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (2, '[{"test": 1234}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (1, '[{"test": 1}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (3, '[{"test": 4}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (4, '[{"test": 5}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (5, '[{"test": 6}]');

INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 1, 1);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 1, 5);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (3, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (4, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (5, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 2, 11);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 2, 15);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (6, 3, 23);
