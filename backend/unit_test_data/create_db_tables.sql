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
        CHECK (type = 'semantic_segmentation' or type = 'instance_segmentation' or type = 'bounding_boxes'),
    default_tool VARCHAR DEFAULT 'freehand' NOT NULL
	    CHECK (default_tool = 'freehand' or default_tool = 'polygon' or default_tool = 'rectangle' or default_tool = 'point' or default_tool = 'circle' or default_tool = 'select')
	    CHECK (allowed_tools LIKE concat('%', default_tool,'%')),
	allowed_tools VARCHAR DEFAULT null,
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

ALTER TABLE input_data ADD COLUMN timestamp_upload TIMESTAMPTZ DEFAULT NULL;
	COMMENT ON COLUMN input_data.timestamp_upload is 'Date when input data item was uploaded';
ALTER TABLE input_data ALTER COLUMN timestamp_upload SET DEFAULT now();

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
    label_task_id INTEGER REFERENCES label_tasks(label_task_id) ON DELETE CASCADE,
    receive_new_unlabeled_data BOOLEAN DEFAULT TRUE);
    COMMENT ON COLUMN users_label_tasks.receive_new_unlabeled_data is 'User is permitted to receive new unlabeled input data items to label';

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

ALTER TABLE labels ADD COLUMN payment_date TIMESTAMPTZ DEFAULT NULL;
	COMMENT ON COLUMN labels.payment_date is 'Date at which this label item is scheduled for payment';
ALTER TABLE labels ADD COLUMN include_in_test_set BOOLEAN DEFAULT FALSE NOT NULL;
	COMMENT ON COLUMN labels.include_in_test_set is 'Include this image in the test set, not training or validation';

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
with t as (
	select distinct on (label_id) * from
	(
		select * from labels
		left outer join label_history using (label_id)
	) as tmp
	order by label_id, timestamp_edit desc
)
select t.*, json_array_length(label_serialised::json) as num_objects_labeled from t;

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
    sum(case when unlabeled = false then 1 else 0 end) as num_labeled,
    sum(case when user_complete = true then 1 else 0 end) as num_user_complete,
    sum(case when needs_improvement = true then 1 else 0 end) as num_needs_improvement,
    sum(case when admin_complete = true then 1 else 0 end) as num_admin_complete,
    sum(case when paid = true then 1 else 0 end) as num_paid
from latest_label_history_per_input_item
group by user_id, label_task_id;

-- show which datasets belong to which dataset groups
create view all_datasets as
with t as (
	select dataset_group_id, d.dataset_id, site, sensor, dataset_description from datasets d
	full outer join dataset_group_lists dgl using(dataset_id)
)
select dg.dataset_group_id, dg.name, dg.description, t.dataset_id, t.site, t.sensor, t.dataset_description from t
full outer join dataset_groups dg using (dataset_group_id);

-- show how many items have been labeled per label task and how many have been approved, paid for, etc
create view label_task_counts as
with t_labeled_counts as (
	select label_task_id, count(*) as labels_used
	from labels
	group by label_task_id
),
t_user_complete as (
	select label_task_id, count(*) AS user_complete
	from labels
	where user_complete = true
		group by label_task_id
),
t_admin_complete as (
	select label_task_id, count(*) AS admin_complete
	from labels
	where admin_complete = true
		group by label_task_id
),
t_needs_improvement as (
	select label_task_id, count(*) AS needs_improvement
	from labels
	where needs_improvement = true
		group by label_task_id
),
t_paid as (
	select label_task_id, count(*) AS paid
	from labels
	where paid = true
		group by label_task_id
),
t_totals as (
	select label_task_id, count(*) AS total_items
	from input_data_per_label_task
	group by label_task_id
)
select * from t_totals
full outer join t_labeled_counts using (label_task_id)
full outer join t_user_complete using (label_task_id)
full outer join t_admin_complete using (label_task_id)
full outer join t_needs_improvement using (label_task_id)
full outer join t_paid using (label_task_id);

-- display number of images per user and label task that are due for payment
create view payments_owed as
with t as (
	select user_id, label_task_id,
	    sum(case when user_complete = true then 1 else 0 end) as num_user_complete,
	    sum(case when admin_complete = true then 1 else 0 end) as num_admin_complete,
	    sum(case when paid = true then 1 else 0 end) as num_paid,
	    sum(num_objects_labeled) as total_objects_labeled
	from latest_label_history_per_input_item
	group by user_id, label_task_id
)
select first_name, last_name, email, organisation, t.*, round(total_objects_labeled * 1.0 / num_user_complete, 2) as mean_objects_per_image, (num_admin_complete-num_paid) as num_payment_owed from t
inner join users using (user_id)
where num_user_complete > 0
order by user_id, label_task_id;

-- display duplicate input data items
create view duplicate_input_data as 
with t_duplicates as (
	select sha1_hash, count(*) from input_data group by sha1_hash having count(*) > 1
)
select * from input_data inner join t_duplicates using (sha1_hash);


