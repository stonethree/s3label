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
INSERT INTO label_tasks(dataset_group_id, title, description, type, is_active) VALUES (2, 'Rock particle segmentation subset', 'Multi-instance segmentation for rock particles', 'instance_segmentation', false);
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
INSERT INTO labels (input_data_id, label_task_id, user_id, admin_complete) VALUES (3, 1, 2, true);
INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress, user_complete, admin_complete) VALUES (4, 1, 3, true, true, true);

INSERT INTO label_history (label_id, label_serialised) VALUES (2, '[{"type": "freehand", "label": "foreground_object", "polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (2, '[{"type": "freehand", "label": "foreground_object", "polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (1, '[{"type": "freehand", "label": "foreground_object", "polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (3, '[{"type": "freehand", "label": "foreground_object", "polygon": {"regions": [[[100, 200], [130, 205], [132, 270], [102, 268]]], "inverted": false}, "selected": true}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (4, '[{"type": "rectangle", "label": {"x": 95, "y": 69.21875, "boxWidth": 260, "boxHeight": 117}, "selected": true, "label_class": "foreground_object"}]');
INSERT INTO label_history (label_id, label_serialised) VALUES (5, '[{"type": "polygon", "label": "foreground_object", "polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]');

INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 1, 1);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 1, 5);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (3, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (4, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (5, 1, 3);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (1, 2, 11);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (2, 2, 15);
INSERT INTO priorities(input_data_id, label_task_id, priority) VALUES (6, 3, 23);
