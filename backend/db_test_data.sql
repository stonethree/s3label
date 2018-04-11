INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_1', 'test_lynxx', 'This is a test. We want to segment rock images');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_2', 'test_lynxx', 'This is a test. We want to segment rock images 2');
INSERT INTO datasets(site, sensor, dataset_description) VALUES ('test_site_3', 'test_froth_sensor', 'This is a test. We want to segment rock images 3');

INSERT INTO dataset_groups(group_name, group_description) VALUES ('Lynxx datasets', 'Some description of why we grouped them...');
INSERT INTO dataset_groups(group_name, group_description) VALUES ('Subset of Lynxx datasets', 'Some description of why we grouped them...2');
INSERT INTO dataset_groups(group_name, group_description) VALUES ('Froth datasets', 'Some description of why we grouped them...3');

INSERT INTO dataset_group_lists(group_id, dataset_id) VALUES (1, 1);
INSERT INTO dataset_group_lists(group_id, dataset_id) VALUES (1, 2);
INSERT INTO dataset_group_lists(group_id, dataset_id) VALUES (2, 1);
INSERT INTO dataset_group_lists(group_id, dataset_id) VALUES (3, 3);

INSERT INTO label_tasks(dataset_group_id, title, description) VALUES (1, 'Rock particle segmentation', 'Multi-instance segmentation for rock particles');
INSERT INTO label_tasks(dataset_group_id, title, description) VALUES (2, 'Rock particle segmentation subset', 'Multi-instance segmentation for rock particles');
INSERT INTO label_tasks(dataset_group_id, title, description) VALUES (3, 'Froth segmentation', 'Multi-instance segmentation for froth bubbles');

INSERT INTO input_data(dataset_id, image_path) VALUES (1, 'test_images/image.jpg');
INSERT INTO input_data(dataset_id, image_path) VALUES (1, 'test_images/image2.jpg');
INSERT INTO input_data(dataset_id, image_path) VALUES (2, 'test_images/image3.jpg');
INSERT INTO input_data(dataset_id, image_path) VALUES (2, 'test_images/image4.jpg');
INSERT INTO input_data(dataset_id, image_path) VALUES (2, 'test_images/image_test.jpg');
INSERT INTO input_data(dataset_id, image_path) VALUES (3, 'test_images/froth_image.jpg');

INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('3Hx45', 'abc', 'Shaun', 'Irwin', 'shaun.irwin@stonethree.com');
INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('79ACF', 'def', 'Kristo', 'Botha', 'kristo.botha@stonethree.com');
INSERT INTO users (user_code, password, first_name, last_name, email) VALUES ('U34DA', 'ghi', 'Jimmy', 'Smith', 'test@gmail.com');

INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) VALUES (1, 1, 1, true);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (2, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 1);

INSERT INTO label_history (label_id, label_serialised) VALUES (2, '{{test: 123}}');

--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 1, 1);
--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 1, 5);
--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (3, 1, 3);
--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (4, 1, 3);
--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (5, 1, 3);
--INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (6, 1, 3);