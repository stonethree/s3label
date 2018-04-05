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

INSERT INTO input_data(dataset_id, image_path, priority) VALUES (1, 'test_images/image.jpg', 1);
INSERT INTO input_data(dataset_id, image_path, priority) VALUES (1, 'test_images/image2.jpg', 5);
INSERT INTO input_data(dataset_id, image_path, priority) VALUES (2, 'test_images/image3.jpg', 6);
INSERT INTO input_data(dataset_id, image_path, priority) VALUES (2, 'test_images/image4.jpg', 6);
INSERT INTO input_data(dataset_id, image_path, priority) VALUES (2, 'test_images/image_test.jpg', 5);
INSERT INTO input_data(dataset_id, image_path, priority) VALUES (3, 'test_images/froth_image.jpg', 3);

INSERT INTO users (user_code, first_name, last_name, email) VALUES ('3Hx45', 'Shaun', 'Irwin', 'shaun.irwin@stonethree.com');
INSERT INTO users (user_code, first_name, last_name, email) VALUES ('79ACF', 'Kristo', 'Botha', 'kristo.botha@stonethree.com');
INSERT INTO users (user_code, first_name, last_name, email) VALUES ('U34DA', 'Jimmy', 'Smith', 'test@gmail.com');

INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) VALUES (1, 1, 1, true);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (2, 1, 1);
INSERT INTO labels (input_data_id, label_task_id, user_id) VALUES (3, 1, 1);

INSERT INTO label_history (label_id, label_serialised) VALUES (2, '{{test: 123}}');