from backend.lib import sql_queries

import pandas as pd


def test_create_new_label_history(refresh_db_every_time, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['input_data_id'] = [1, 2, 3, 4, 5]
    df_test['dataset_group_id'] = [1, 1, 1, 1, 1]
    df_test['dataset_id'] = [1, 1, 2, 2, 2]

    engine = db_connection_sqlalchemy
    label_hist_id = sql_queries.create_new_label_history(engine,
                                                         label_id=1,
                                                         serialised_label='{"unit_test_example": 1238}')

    assert label_hist_id == 7


def test_create_new_label_when_label_already_exists(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.create_new_label(engine, input_data_id=3, label_task_id=1, user_id=1)

    assert label_id == 3


def test_create_new_label_when_label_does_not_yet_exist(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.create_new_label(engine, input_data_id=4, label_task_id=1, user_id=4)

    assert label_id == 7
