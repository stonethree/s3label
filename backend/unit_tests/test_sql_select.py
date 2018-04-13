from backend.lib import sql_queries

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal


def test_get_all_input_data_items(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [1, 2, 3, 4, 5]
    df_test['dataset_group_id'] = [1, 1, 1, 1, 1]
    df_test['dataset_id'] = [1, 1, 2, 2, 2]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_input_data_items(engine, label_task_id=1)

    assert_frame_equal(df, df_test)


def test_get_next_unlabeled_input_data_item(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    input_data_id = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=1)

    assert input_data_id == 3


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
