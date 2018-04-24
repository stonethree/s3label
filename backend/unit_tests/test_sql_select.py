from backend.lib import sql_queries

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal


def test_get_user_info_for_existing_user(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_id = sql_queries.get_user_id(engine, email='shaun.irwin@stonethree.com', password='abc')

    assert user_id == 1


def test_get_user_info_with_wrong_password_results_in_no_users_found(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_id = sql_queries.get_user_id(engine, email='shaun.irwin@stonethree.com', password='abcd')

    assert user_id is None


def test_get_user_info_with_wildcard_email_address_results_in_no_users_found(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_id = sql_queries.get_user_id(engine, email='*', password='abcd')

    assert user_id is None


def test_get_user_info_with_wildcard_password_results_in_no_users_found(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_id = sql_queries.get_user_id(engine, email='shaun.irwin@stonethree.com', password='*')

    assert user_id is None


def test_get_user_info_for_non_existant_user(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_id = sql_queries.get_user_id(engine, email='something@stonethree.com', password='abc')

    assert user_id is None


def test_get_all_input_data_items(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [1, 2, 3, 4, 5]
    df_test['dataset_group_id'] = [1, 1, 1, 1, 1]
    df_test['dataset_id'] = [1, 1, 2, 2, 2]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_input_data_items(engine, label_task_id=1)

    assert_frame_equal(df, df_test)


def test_get_all_user_input_data(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [3, 2, 1]
    df_test['input_data_id'] = [3, 2, 1]
    df_test['user_id'] = [1, 1, 1]
    df_test['label_task_id'] = [1, 1, 1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_user_input_data(engine, user_id=1, label_task_id=1, n=None)

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])


def test_get_preceding_user_data_item(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [2]
    df_test['input_data_id'] = [2]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_preceding_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=3)

    assert df['label_id'].values == df_test['label_id'].values
    assert df['input_data_id'].values == df_test['input_data_id'].values
    assert df['user_id'].values == df_test['user_id'].values
    assert df['label_task_id'].values == df_test['label_task_id'].values


def test_get_preceding_user_data_item_for_another_input_data_id(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [1]
    df_test['input_data_id'] = [1]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_preceding_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=2)

    assert df['label_id'].values == df_test['label_id'].values
    assert df['input_data_id'].values == df_test['input_data_id'].values
    assert df['user_id'].values == df_test['user_id'].values
    assert df['label_task_id'].values == df_test['label_task_id'].values


def test_get_preceding_user_data_item_if_last_item(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_preceding_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=1)

    assert len(df) == 0


def test_get_preceding_user_data_item_if_input_data_id_not_found(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_preceding_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=28)

    assert len(df) == 0


def test_get_next_unlabeled_input_data_item(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    input_data_id = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=1)

    assert input_data_id == 5


def test_get_all_input_data_items_if_input_data_id_does_not_exist(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = []
    df_test['dataset_group_id'] = []
    df_test['dataset_id'] = []

    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_input_data_items(engine, label_task_id=27)

    assert len(df) == 0
    assert df.columns.tolist() == df_test.columns.tolist()


def test_get_input_data_path(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    input_data_path = sql_queries.get_input_data_path(engine, input_data_id=1)

    assert input_data_path == 'test_images/image.jpg'


def test_get_input_data_path_if_input_data_id_does_not_exist(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    input_data_path = sql_queries.get_input_data_path(engine, input_data_id=27)

    assert input_data_path is None


def test_get_label_tasks(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_task_id'] = [1, 2, 3, 4]
    df_test['dataset_group_id'] = [1, 2, 3, 3]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label_tasks(engine)

    expected_cols = ['label_task_id',
                     'dataset_group_id',
                     'title',
                     'description',
                     'type',
                     'example_labeling',
                     'default_tool',
                     'permit_overlap',
                     'label_classes']

    assert df.columns.tolist() == expected_cols
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])


def test_get_label_id(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.get_label_id(engine, user_id=1, label_task_id=1, input_data_id=1)

    assert label_id == 1


def test_get_label_id_if_label_does_not_exist(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.get_label_id(engine, user_id=1, label_task_id=1, input_data_id=27)

    assert label_id is None


def test_get_recent_labeled_input_data(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [2, 3]
    df_test['label_task_id'] = [1, 1]
    df_test['label_id'] = [2, 3]
    df_test['user_id'] = [1, 1]
    df_test['in_progress'] = [False, False]
    df_test['label_history_id'] = [1, 4]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_recent_labeled_input_data(engine,
                                                   user_id=1,
                                                   label_task_id=1,
                                                   input_data_id=2,
                                                   n=4,
                                                   include_current_input_data=True)

    assert len(df) == 2
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])
    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['label_history_id'], df_test['label_history_id'])


def test_get_recent_labeled_input_data_if_only_one_item_requested(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [3]
    df_test['label_task_id'] = [1]
    df_test['label_id'] = [3]
    df_test['user_id'] = [1]
    df_test['in_progress'] = [False]
    df_test['label_history_id'] = [4]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_recent_labeled_input_data(engine,
                                                   user_id=1,
                                                   label_task_id=1,
                                                   input_data_id=2,
                                                   n=1,
                                                   include_current_input_data=True)

    assert len(df) == 1
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])
    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['label_history_id'], df_test['label_history_id'])


def test_get_recent_labeled_input_data_if_not_including_specified_input_data_id(refresh_db_once,
                                                                                db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [2]
    df_test['label_task_id'] = [1]
    df_test['label_id'] = [2]
    df_test['user_id'] = [1]
    df_test['in_progress'] = [False]
    df_test['label_history_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_recent_labeled_input_data(engine,
                                                   user_id=1,
                                                   label_task_id=1,
                                                   input_data_id=2,
                                                   n=4,
                                                   include_current_input_data=False)

    assert len(df) == 1
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])
    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['label_history_id'], df_test['label_history_id'])
