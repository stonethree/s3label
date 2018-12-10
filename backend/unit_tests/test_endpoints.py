from .unit_test_utils import json_of_response, nans_to_nones, AuthActions
from backend.lib import data_download as dd

import pandas as pd
import json
from PIL import Image
import io
import os


def test_server_exists(client, refresh_db_once):
    rv = client.get('/')

    assert rv.status_code == 200

    resp = json_of_response(rv)

    assert 'message' in resp.keys()
    assert resp['message'] == 'You have found the S3 Label image server!'


def test_login_logout(auth, refresh_db_once):
    rv_login = auth.login()

    assert rv_login.status_code == 200

    rv_label_tasks = auth.client.get(auth.base_url + '/label_tasks')

    assert rv_label_tasks.status_code == 401

    rv_label_tasks = auth.client.get(auth.base_url + '/label_tasks', headers=auth.auth_header())

    assert rv_label_tasks.status_code == 200


def test_find_missing_input_data(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/missing_input_data',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert response['num_paths_total'] == 6
    assert response['num_missing_paths'] == 0


def test_get_label_tasks(auth, refresh_db_once):
    auth.login()

    rv_label_tasks = auth.client.get(auth.base_url + '/label_tasks', headers=auth.auth_header())

    assert rv_label_tasks.status_code == 200

    label_tasks = json_of_response(rv_label_tasks)

    assert label_tasks[0]['label_task_id'] == 1
    assert label_tasks[0]['title'] == 'Rock particle segmentation'


def test_get_label(auth, refresh_db_once):
    auth.login()

    rv_label = auth.client.get(auth.base_url + '/labels/6', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label['user_id'] == 3
    assert label['in_progress'] is True
    assert label['user_complete'] is True
    assert label['admin_complete'] is True
    assert label['paid'] is False


def test_get_latest_label_history_for_logged_in_user(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv_label = auth.client.get(auth.base_url + '/labels/input_data/3/label_tasks/1', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label[0]['label_id'] == 3
    assert label[0]['label_serialised'] == '[{"type": "freehand", "label": "foreground_object", "polygon": ' \
                                           '{"regions": [[[100, 200], [130, 205], [132, 270], [102, 268]]], ' \
                                           '"inverted": false}, "selected": true}]'
    assert label[0]['input_data_id'] == 3
    assert label[0]['label_task_id'] == 1
    assert label[0]['user_id'] == 1


def test_get_latest_label_history_for_different_logged_in_user(auth, refresh_db_once):
    auth.login(email='kristo.botha@stonethree.com', password='def')

    rv_label = auth.client.get(auth.base_url + '/labels/input_data/3/label_tasks/1', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label[0]['label_id'] == 5
    assert label[0]['label_serialised'] == '[{"type": "polygon", "label": "foreground_object", ' \
                                           '"polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], ' \
                                           '[132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]'
    assert label[0]['input_data_id'] == 3
    assert label[0]['label_task_id'] == 1
    assert label[0]['user_id'] == 2


def test_get_latest_label_history_for_specified_user(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv_label = auth.client.get(auth.base_url + '/labels/input_data/3/label_tasks/1/users/1', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label[0]['label_id'] == 3
    assert label[0]['label_serialised'] == '[{"type": "freehand", "label": "foreground_object", "polygon": ' \
                                           '{"regions": [[[100, 200], [130, 205], [132, 270], [102, 268]]], ' \
                                           '"inverted": false}, "selected": true}]'
    assert label[0]['input_data_id'] == 3
    assert label[0]['label_task_id'] == 1
    assert label[0]['user_id'] == 1

    rv_label = auth.client.get(auth.base_url + '/labels/input_data/3/label_tasks/1/users/2', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label[0]['label_id'] == 5
    assert label[0]['label_serialised'] == '[{"type": "polygon", "label": "foreground_object", ' \
                                           '"polygon": {"regions": [[[100.2, 200.1], [130.4, 205.1], ' \
                                           '[132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]'
    assert label[0]['input_data_id'] == 3
    assert label[0]['label_task_id'] == 1
    assert label[0]['user_id'] == 2


def test_get_datasets(auth, refresh_db_once):
    auth.login()

    rv_datasets = auth.client.get(auth.base_url + '/datasets', headers=auth.auth_header())

    assert rv_datasets.status_code == 200

    datasets = json_of_response(rv_datasets)

    assert len(datasets) == 4
    assert datasets[0]['dataset_id'] == 1
    assert datasets[0]['site'] == 'test_site_1'
    assert datasets[0]['sensor'] == 'test_lynxx'
    assert datasets[0]['dataset_description'] == 'This is a test. We want to segment rock images'


def test_get_label_examples(auth, refresh_db_once):
    auth.login()

    rv_examples = auth.client.get(auth.base_url + '/examples/label_tasks/1', headers=auth.auth_header())

    assert rv_examples.status_code == 200

    examples = json_of_response(rv_examples)

    assert len(examples) == 2
    assert examples[0]['example_labeling_id'] == 1
    assert examples[0]['title'] == 'Example of good labeling'
    assert examples[0]['description'] == 'Here you can see a well labeled image'
    # assert examples[0]['image_path'] == 'unit_test_data/example_1.jpg'
    assert 'image_path' not in examples[0].keys()


def test_count_input_data_items_per_user_per_label_task_as_non_admin(auth, refresh_db_once):
    auth.login()

    rv_counts = auth.client.get(auth.base_url + '/item_counts?user_id=3', headers=auth.auth_header())

    assert rv_counts.status_code == 200

    item_counts = json_of_response(rv_counts)

    df_item_counts = pd.DataFrame(item_counts)
    df_item_counts = nans_to_nones(df_item_counts)

    assert df_item_counts['user_id'].tolist() == [3]
    assert df_item_counts['label_task_id'].tolist() == [1]
    assert df_item_counts['total_items'].tolist() == [1]
    assert df_item_counts['num_labeled'].tolist() == [1]
    assert df_item_counts['num_user_complete'].tolist() == [1]
    assert df_item_counts['num_needs_improvement'].tolist() == [0]
    assert df_item_counts['num_admin_complete'].tolist() == [1]
    assert df_item_counts['num_paid'].tolist() == [0]


def test_count_input_data_items_per_user_per_label_task_as_admin(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv_counts = auth.client.get(auth.base_url + '/item_counts', headers=auth.auth_header())

    assert rv_counts.status_code == 200

    item_counts = json_of_response(rv_counts)

    df_item_counts = pd.DataFrame(item_counts)
    df_item_counts = nans_to_nones(df_item_counts)

    assert df_item_counts['user_id'].tolist() == [1, 1, 1, 1, 2, 2, 2, 3, None, None]
    assert df_item_counts['label_task_id'].tolist() == [1, 2, 3, 5, 1, 2, 5, 1, 4, 6]
    assert df_item_counts['total_items'].tolist() == [5, 3, 1, 5, 5, 2, 5, 1, 1, 1]
    assert df_item_counts['num_labeled'].tolist() == [3, 1, 0, 0, 1, 0, 0, 1, 0, 0]


def test_get_next_unlabeled_image(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    # request first image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 1
    assert next_im['label_id'] == 7

    # request second image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 2
    assert next_im['label_id'] == 8

    # request third image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 3
    assert next_im['label_id'] == 9

    # request fourth image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 4
    assert next_im['label_id'] == 10

    # request fifth image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 5
    assert next_im['label_id'] == 11

    # request sixth image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 404


def test_get_next_unlabeled_image_for_multiple_users_labeling_same_label_task(client, refresh_db_every_time):
    auth_1 = AuthActions(client)
    auth_2 = AuthActions(client)
    auth_1.login(email='shaun.irwin@stonethree.com', password='abc')
    auth_2.login(email='kristo.botha@stonethree.com', password='def')

    # request first image (user 1)

    rv_next_im = auth_1.client.get(auth_1.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_1.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 1
    assert next_im['label_id'] == 7

    # request second image (user 1)

    rv_next_im = auth_1.client.get(auth_1.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_1.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 2
    assert next_im['label_id'] == 8

    # request third image (user 2)

    rv_next_im = auth_2.client.get(auth_2.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_2.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 3
    assert next_im['label_id'] == 9

    # request fourth image (user 2)

    rv_next_im = auth_2.client.get(auth_2.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_2.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 4
    assert next_im['label_id'] == 10

    # request fifth image (user 2)

    rv_next_im = auth_2.client.get(auth_2.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_2.auth_header())

    assert rv_next_im.status_code == 200

    next_im = json_of_response(rv_next_im)

    assert next_im['input_data_id'] == 5
    assert next_im['label_id'] == 11

    # request sixth image (user 2)

    rv_next_im = auth_2.client.get(auth_2.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_2.auth_header())

    assert rv_next_im.status_code == 404

    # request sixth image (user 2)

    rv_next_im = auth_1.client.get(auth_1.base_url + '/unlabeled_images/label_tasks/5?shuffle=false&limit=1',
                                   headers=auth_1.auth_header())

    assert rv_next_im.status_code == 404


def test_get_next_unlabeled_image_for_label_task_without_images(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    # request first image

    rv_next_im = auth.client.get(auth.base_url + '/unlabeled_images/label_tasks/6?shuffle=false&limit=1',
                                 headers=auth.auth_header())

    assert rv_next_im.status_code == 404


def test_update_label_fields_as_admin_user(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    # update fields of label

    rv = auth.client.patch(auth.base_url + '/labels/6',
                           headers=auth.auth_header(),
                           data=json.dumps({'user_complete': True, 'admin_complete': True}),
                           content_type='application/json')

    assert rv.status_code == 200

    rv_label = auth.client.get(auth.base_url + '/labels/6', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label['user_id'] == 3
    assert label['in_progress'] is True
    assert label['user_complete'] is True
    assert label['admin_complete'] is True
    assert label['needs_improvement'] is False
    assert label['paid'] is False

    # update other fields of label

    rv = auth.client.patch(auth.base_url + '/labels/6',
                           headers=auth.auth_header(),
                           data=json.dumps({'needs_improvement': True, 'paid': True}),
                           content_type='application/json')

    assert rv.status_code == 200

    rv_label = auth.client.get(auth.base_url + '/labels/6', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label['user_id'] == 3
    assert label['in_progress'] is True
    assert label['user_complete'] is True
    assert label['admin_complete'] is True
    assert label['needs_improvement'] is True
    assert label['paid'] is True


def test_update_label_fields_as_non_admin_user(auth, refresh_db_every_time):
    auth.login()

    # update fields of label

    rv = auth.client.patch(auth.base_url + '/labels/6',
                           headers=auth.auth_header(),
                           data=json.dumps({'user_complete': True}),
                           content_type='application/json')

    assert rv.status_code == 200

    rv_label = auth.client.get(auth.base_url + '/labels/6', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label['user_complete'] is True

    # update other fields of label

    rv = auth.client.patch(auth.base_url + '/labels/6',
                           headers=auth.auth_header(),
                           data=json.dumps({'user_complete': False}),
                           content_type='application/json')

    assert rv.status_code == 200

    rv_label = auth.client.get(auth.base_url + '/labels/6', headers=auth.auth_header())

    assert rv_label.status_code == 200

    label = json_of_response(rv_label)

    assert label['user_complete'] is False


def test_update_label_fields_as_non_admin_user_fails_if_label_was_created_by_another_user(auth, refresh_db_every_time):
    auth.login()

    # update fields of label

    rv = auth.client.patch(auth.base_url + '/labels/5',
                           headers=auth.auth_header(),
                           data=json.dumps({'user_complete': True}),
                           content_type='application/json')

    assert rv.status_code == 403


def test_update_label_fields_as_non_admin_user_fails_if_updating_admin_only_field(auth, refresh_db_every_time):
    auth.login()

    # update fields of label

    rv = auth.client.patch(auth.base_url + '/labels/6',
                           headers=auth.auth_header(),
                           data=json.dumps({'paid': True}),
                           content_type='application/json')

    assert rv.status_code == 403


def test_get_paths_of_images_in_folder(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/image_paths?folder_path=test_images&recursive=false',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert len(response['image_paths']) == 6
    assert response['image_paths'][0] == r'test_images/froth_image.jpg'
    assert response['image_paths'][1] == r'test_images/image.jpg'


def test_get_paths_of_images_in_folder_recursive(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/image_paths?folder_path=test_images&recursive=true',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert len(response['image_paths']) == 7
    assert response['image_paths'][0] == r'test_images/another_folder/image_copy.jpg'
    assert response['image_paths'][1] == r'test_images/froth_image.jpg'
    assert response['image_paths'][2] == r'test_images/image.jpg'


def test_get_paths_of_images_in_folder_only_admin_allowed(auth, refresh_db_once):
    auth.login()

    rv = auth.client.get(auth.base_url + '/image_paths?folder_path=test_images',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 403


def test_get_paths_of_images_in_folder_returns_error_if_path_invalid(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/image_paths?folder_path=does_not_exist',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 400


def test_get_paths_of_images_in_folder_returns_error_if_no_path_specified(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/image_paths',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 400


def test_upload_new_input_data_item(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.post(auth.base_url + '/input_data',
                          headers=auth.auth_header(),
                          data=json.dumps({'input_data_path': 'test_images/another_folder/image_copy.jpg',
                                           'dataset_id': 1}),
                          content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert response['input_data_id'] == 7

    rv = auth.client.post(auth.base_url + '/input_data',
                          headers=auth.auth_header(),
                          data=json.dumps({'input_data_path': 'test_images/another_folder/image_copy.jpg',
                                           'dataset_id': 1}),
                          content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert response['input_data_id'] == 8


def test_get_image(auth, refresh_db_once):
    auth.login()

    rv_image = auth.client.get(auth.base_url + '/input_images/2', headers=auth.auth_header())

    assert rv_image.status_code == 200
    assert rv_image.mimetype == 'image/jpeg'

    im = Image.open(io.BytesIO(rv_image.data))

    assert im.width == 640
    assert im.height == 480
    assert im.layers == 3


def test_get_image_low_resolution_specifying_height(auth, refresh_db_once):
    auth.login()

    rv_image = auth.client.get(auth.base_url + '/input_images/2?height=150', headers=auth.auth_header())

    assert rv_image.status_code == 200
    assert rv_image.mimetype == 'image/jpeg'

    im = Image.open(io.BytesIO(rv_image.data))

    assert im.width == 200
    assert im.height == 150
    assert im.layers == 3


def test_get_image_low_resolution_specifying_width(auth, refresh_db_once):
    auth.login()

    rv_image = auth.client.get(auth.base_url + '/input_images/2?width=200', headers=auth.auth_header())

    assert rv_image.status_code == 200
    assert rv_image.mimetype == 'image/jpeg'

    im = Image.open(io.BytesIO(rv_image.data))

    assert im.width == 200
    assert im.height == 150
    assert im.layers == 3


def test_download_ground_truth_images_to_disk(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.put(auth.base_url + '/label_images/label_task_id/1',
                         headers=auth.auth_header(),
                         data=json.dumps({'output_folder': 'tmp/ground_truth_images',
                                          'prefix': 'im_',
                                          'suffix': '_gt2'}),
                         content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert response['total_labels_found'] == 2
    assert response['num_ground_truth_images'] == 1

    assert os.path.exists('tmp/ground_truth_images/im_input_data_id_3_label_id_5_gt2.png')

    assert dd.get_image_dims('tmp/ground_truth_images/im_input_data_id_3_label_id_5_gt2.png') == (640, 428)

    assert os.path.exists('tmp/ground_truth_images/labels_info.csv')


def test_get_all_latest_label_history_for_a_label_task(auth, refresh_db_every_time):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.post(auth.base_url + '/latest_label_history/label_task_id/1',
                          headers=auth.auth_header(),
                          data=json.dumps({'test_data': 'false',
                                           'label_status': 'admin_complete'}),
                          content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    df = pd.DataFrame(response)

    expected_label = """[{"type": "polygon", "label": "foreground_object", "polygon": {"regions": """ + \
"""[[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]"""

    assert df.loc[:, 'data_path'].tolist() == ['test_images/image3.jpg', 'test_images/image4.jpg']
    assert df.loc[:, 'input_data_id'].tolist() == [3, 4]
    assert df.loc[:, 'label_id'].tolist() == [5, 6]
    assert df.loc[:, 'dataset_id'].tolist() == [2, 2]
    assert df.loc[:, 'label_serialised'].tolist() == [expected_label, None]
    assert df.loc[:, 'include_in_test_set'].tolist() == [False, False]
    assert df.loc[:, 'admin_complete'].tolist() == [True, True]
    # assert df.loc[:, 'label_history_id'].tolist() == [6, None]
    # assert df.loc[:, 'num_objects_labeled'].tolist() == [1, 0]
