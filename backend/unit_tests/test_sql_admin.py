from backend.lib import sql_queries_admin

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal


def test_is_user_an_admin_if_user_is_in_fact_admin(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_is_admin = sql_queries_admin.is_user_an_admin(engine, user_id=1)
    assert user_is_admin


def test_is_user_an_admin_if_user_just_a_regular_user(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_is_admin = sql_queries_admin.is_user_an_admin(engine, user_id=3)
    assert not user_is_admin


def test_is_user_an_admin_if_user_id_does_not_exist(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    user_is_admin = sql_queries_admin.is_user_an_admin(engine, user_id=28)
    assert user_is_admin is None


def test_get_users(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['user_id'] = [1, 2, 3, 4]
    df_test['first_name'] = ['Shaun', 'Kristo', 'Jimmy', 'Marcus']
    df_test['last_name'] = ['Irwin', 'Botha', 'Smith', 'Octavius']
    df_test['email'] = ['shaun.irwin@stonethree.com', 'kristo.botha@stonethree.com', 'test@gmail.com',
                        'test2@gmail.com']
    df_test['organisation'] = [None, None, None, None]
    df_test['note'] = [None, None, None, None]
    df_test['is_admin'] = [True, True, False, False]

    engine = db_connection_sqlalchemy
    df = sql_queries_admin.get_users(engine)

    assert_frame_equal(df, df_test)


def test_get_label_task_ids_for_a_user(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_task_id'] = [1, 2]

    engine = db_connection_sqlalchemy
    df = sql_queries_admin.get_label_task_ids_for_a_user(engine, user_id=1)

    assert_frame_equal(df, df_test)


def test_get_labeled_data_for_user_and_task(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [3, 2, 1]
    df_test['label_history_id'] = [4, 1, 3]
    df_test['input_data_id'] = [3, 2, 1]

    cols = ['label_id',
            'label_history_id',
            'label_task_id',
            'input_data_id',
            'dataset_id',
            'dataset_group_id',
            'priority',
            'in_progress',
            'user_complete',
            'admin_complete',
            'paid',
            'user_comment',
            'admin_comment',
            'timestamp_edit',
            'label_serialised']

    engine = db_connection_sqlalchemy
    df = sql_queries_admin.get_labeled_data_for_user_and_task(engine, user_id=1, label_task_id=1)

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['label_history_id'], df_test['label_history_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])

    for col in cols:
        assert col in df.columns.tolist()

