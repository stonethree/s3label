from .unit_test_utils import json_of_response, nans_to_nones

import pandas as pd
import json


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
    assert label['user_complete'] is False
    assert label['admin_complete'] is False


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
    assert df_item_counts['num_unlabeled'].tolist() == [0]
    assert df_item_counts['num_labeled'].tolist() == [1]


def test_count_input_data_items_per_user_per_label_task_as_admin(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv_counts = auth.client.get(auth.base_url + '/item_counts', headers=auth.auth_header())

    assert rv_counts.status_code == 200

    item_counts = json_of_response(rv_counts)

    df_item_counts = pd.DataFrame(item_counts)
    df_item_counts = nans_to_nones(df_item_counts)

    assert df_item_counts['user_id'].tolist() == [1, 1, 1, 1, 2, 2, 3, None, None]
    assert df_item_counts['label_task_id'].tolist() == [1, 2, 3, 5, 1, 2, 1, 4, 6]
    assert df_item_counts['total_items'].tolist() == [5, 3, 1, 5, 1, 4, 1, 1, 1]
    assert df_item_counts['num_unlabeled'].tolist() == [2, 2, 1, 5, 0, 4, 0, 1, 1]
    assert df_item_counts['num_labeled'].tolist() == [3, 1, 0, 0, 1, 0, 1, 0, 0]


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
    assert response['image_paths'][0] == r'test_images\froth_image.jpg'
    assert response['image_paths'][1] == r'test_images\image.jpg'


def test_get_paths_of_images_in_folder_recursive(auth, refresh_db_once):
    auth.login(email='shaun.irwin@stonethree.com', password='abc')

    rv = auth.client.get(auth.base_url + '/image_paths?folder_path=test_images&recursive=true',
                         headers=auth.auth_header(),
                         content_type='application/json')

    assert rv.status_code == 200

    response = json_of_response(rv)

    assert len(response['image_paths']) == 7
    assert response['image_paths'][0] == r'test_images\another_folder\image_copy.jpg'
    assert response['image_paths'][1] == r'test_images\froth_image.jpg'
    assert response['image_paths'][2] == r'test_images\image.jpg'


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
