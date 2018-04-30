from .unit_test_utils import json_of_response


def test_server_exists(client, refresh_db_once):
    rv = client.get('/')

    assert rv.status_code == 200

    resp = json_of_response(rv)

    assert 'message' in resp.keys()
    assert resp['message'] == 'You have found the S3 Label image server!'


def test_login_logout(auth, refresh_db_once):
    rv_login = auth.login()

    assert rv_login.status_code == 200

    rv_get_tasks = auth.client.get(auth.base_url + '/label_tasks')

    assert rv_get_tasks.status_code == 401

    rv_get_tasks = auth.client.get(auth.base_url + '/label_tasks', headers=auth.auth_header())

    assert rv_get_tasks.status_code == 200


def test_get_label_tasks(auth, refresh_db_once):
    auth.login()

    rv_get_tasks = auth.client.get(auth.base_url + '/label_tasks', headers=auth.auth_header())

    assert rv_get_tasks.status_code == 200

    label_tasks = json_of_response(rv_get_tasks)

    assert label_tasks[0]['label_task_id'] == 1
    assert label_tasks[0]['title'] == 'Rock particle segmentation'


# def test_get_next_unlabeled_image(auth):
#     auth.login()
#
#     rv_get_tasks = auth.client.get(auth.base_url + '/label_tasks', headers=auth.auth_header())
#
#     assert rv_get_tasks.status_code == 200
#
#     label_tasks = json_of_response(rv_get_tasks)
#
#     assert label_tasks[0]['label_task_id'] == 1
#     assert label_tasks[0]['title'] == 'Rock particle segmentation'