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


def test_count_input_data_items_for_all_users_and_label_tasks(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['user_id'] = [1, 1, 1, 1, 2, 2, 2, 3, None, None]
    df_test['label_task_id'] = [1, 2, 3, 5, 1, 2, 5, 1, 4, 6]
    df_test['total_items'] = [5, 3, 1, 5, 5, 2, 5, 1, 1, 1]
    df_test['num_unlabeled'] = [2, 2, 1, 5, 4, 2, 5, 0, 1, 1]
    df_test['num_labeled'] = [3, 1, 0, 0, 1, 0, 0, 1, 0, 0]

    engine = db_connection_sqlalchemy
    df = sql_queries.count_input_data_items_per_user_per_label_task(engine, label_task_id=None, user_id=None)

    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])
    assert_series_equal(df['total_items'], df_test['total_items'])
    assert_series_equal(df['num_labeled'], df_test['num_labeled'])


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
    
    
def test_get_all_user_input_data_filtered(refresh_db_once, db_connection_sqlalchemy):
    #filter incomplete
    df_test = pd.DataFrame()
    df_test['label_id'] = [1]
    df_test['input_data_id'] = [1]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_first_user_input_data(engine, user_id=1, label_task_id=1, label_filter = "filter_incomplete")
    
    print("Received first incomplete entry")

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['user_id'], df_test['user_id'])
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])
    
    #filter complete
    df_test = pd.DataFrame()
    df_test['label_id'] = [6]
    df_test['input_data_id'] = [4]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [3]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_first_user_input_data(engine, user_id=3, label_task_id=1, label_filter = "filter_complete")

    assert len(df) == 0  
 

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


def test_get_next_user_data_item(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [3]
    df_test['input_data_id'] = [3]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_next_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=2)

    assert df['label_id'].values == df_test['label_id'].values
    assert df['input_data_id'].values == df_test['input_data_id'].values
    assert df['user_id'].values == df_test['user_id'].values
    assert df['label_task_id'].values == df_test['label_task_id'].values


def test_get_next_user_data_item_for_another_input_data_id(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [2]
    df_test['input_data_id'] = [2]
    df_test['user_id'] = [1]
    df_test['label_task_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_next_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=1)

    assert df['label_id'].values == df_test['label_id'].values
    assert df['input_data_id'].values == df_test['input_data_id'].values
    assert df['user_id'].values == df_test['user_id'].values
    assert df['label_task_id'].values == df_test['label_task_id'].values


def test_get_next_user_data_item_if_first_item(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_next_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=3)

    assert len(df) == 0


def test_get_next_user_data_item_if_input_data_id_not_found(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_next_user_data_item(engine, user_id=1, label_task_id=1, current_input_data_id=28)

    assert len(df) == 0


def test_get_next_unlabeled_input_data_item(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df_unlabeled = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=5, shuffle=False, n=None)

    assert len(df_unlabeled) == 5
    assert df_unlabeled['input_data_id'][0] == 1
    assert df_unlabeled['input_data_id'][1] == 2
    assert df_unlabeled['input_data_id'][2] == 3
    assert df_unlabeled['input_data_id'][3] == 4
    assert df_unlabeled['input_data_id'][4] == 5


def test_get_next_unlabeled_input_data_item_with_limit(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df_unlabeled = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=5, shuffle=False, n=2)

    assert len(df_unlabeled) == 2
    assert df_unlabeled['input_data_id'][0] == 1
    assert df_unlabeled['input_data_id'][1] == 2


def test_get_next_unlabeled_input_data_item_when_some_images_already_labeled_for_a_label_task(refresh_db_once,
                                                                                              db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df_unlabeled = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=1, shuffle=False, n=None)

    assert len(df_unlabeled) == 1
    assert df_unlabeled['input_data_id'][0] == 5


def test_get_next_unlabeled_input_data_item_when_no_images_available(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df_unlabeled = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id=6, shuffle=False, n=None)

    assert df_unlabeled is None


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
    df_test['label_task_id'] = [1, 2, 3, 4, 5, 6]
    df_test['dataset_group_id'] = [1, 2, 3, 3, 1, 4]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label_tasks(engine)

    expected_cols = ['label_task_id',
                     'dataset_group_id',
                     'title',
                     'description',
                     'type',
                     'default_tool',
                     'allowed_tools',
                     'permit_overlap',
                     'label_classes']

    assert df.columns.tolist() == expected_cols
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])


def test_get_label_tasks_for_specific_user(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_task_id'] = [1, 2, 3, 5]
    df_test['dataset_group_id'] = [1, 2, 3, 1]
    df_test['title'] = ['Rock particle segmentation',
                        'Rock particle segmentation subset',
                        'Froth segmentation',
                        'Rock particle segmentation: Initially unlabeled']

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label_tasks(engine, user_id=1)

    expected_cols = ['label_task_id',
                     'dataset_group_id',
                     'title',
                     'description',
                     'type',
                     'default_tool',
                     'allowed_tools',
                     'permit_overlap',
                     'label_classes']

    assert df.columns.tolist() == expected_cols
    assert_series_equal(df['label_task_id'], df_test['label_task_id'])


def test_get_label_task(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_task_id'] = [1]
    df_test['dataset_group_id'] = [1]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label_task(engine, label_task_id=1)

    expected_cols = ['label_task_id',
                     'dataset_group_id',
                     'title',
                     'description',
                     'type',
                     'default_tool',
                     'allowed_tools',
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


def test_get_label(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [3]
    df_test['input_data_id'] = [3]
    df_test['in_progress'] = [False]
    df_test['user_complete'] = [False]
    df_test['needs_improvement'] = [False]
    df_test['admin_complete'] = [False]
    df_test['paid'] = [False]
    df_test['user_comment'] = [None]
    df_test['admin_comment'] = [None]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['user_complete'], df_test['user_complete'])
    assert_series_equal(df['needs_improvement'], df_test['needs_improvement'])
    assert_series_equal(df['admin_complete'], df_test['admin_complete'])
    assert_series_equal(df['paid'], df_test['paid'])
    assert_series_equal(df['user_comment'], df_test['user_comment'])
    assert_series_equal(df['admin_comment'], df_test['admin_comment'])


def test_get_label_by_id(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [3]
    df_test['input_data_id'] = [3]
    df_test['in_progress'] = [False]
    df_test['user_complete'] = [False]
    df_test['needs_improvement'] = [False]
    df_test['admin_complete'] = [False]
    df_test['paid'] = [False]
    df_test['user_comment'] = [None]
    df_test['admin_comment'] = [None]

    engine = db_connection_sqlalchemy
    df = sql_queries.get_label_by_id(engine, label_id=3)

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['user_complete'], df_test['user_complete'])
    assert_series_equal(df['needs_improvement'], df_test['needs_improvement'])
    assert_series_equal(df['admin_complete'], df_test['admin_complete'])
    assert_series_equal(df['paid'], df_test['paid'])
    assert_series_equal(df['user_comment'], df_test['user_comment'])
    assert_series_equal(df['admin_comment'], df_test['admin_comment'])


def test_get_latest_label(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['label_id'] = [4]
    df_test['input_data_id'] = [3]
    df_test['in_progress'] = [False]
    df_test['label_serialised'] = ['[{"type": "rectangle", "label": {"x": 95, "y": 69.21875, '
                                   '"boxWidth": 260, "boxHeight": 117}, "selected": true, '
                                   '"label_class": "foreground_object"}]']

    engine = db_connection_sqlalchemy
    df = sql_queries.get_latest_label(engine, user_id=1, label_task_id=2, input_data_id=3)

    assert_series_equal(df['label_id'], df_test['label_id'])
    assert_series_equal(df['input_data_id'], df_test['input_data_id'])
    assert_series_equal(df['in_progress'], df_test['in_progress'])
    assert_series_equal(df['label_serialised'], df_test['label_serialised'])


def test_get_example_labelings(refresh_db_once, db_connection_sqlalchemy):
    df_test = pd.DataFrame()
    df_test['example_labeling_id'] = [1, 2]
    df_test['title'] = ['Example of good labeling', 'Example of bad labeling']

    engine = db_connection_sqlalchemy
    df = sql_queries.get_example_labelings(engine, label_task_id=1)

    expected_cols = ['example_labeling_id',
                     'title',
                     'description']

    assert df.columns.tolist() == expected_cols
    assert_series_equal(df['example_labeling_id'], df_test['example_labeling_id'])
    assert_series_equal(df['title'], df_test['title'])


def test_get_all_completed_labels(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_completed_labels(engine, label_task_id=1, dataset_id=None)

    assert len(df) == 2
    assert df['admin_complete'][0]
    assert df['label_task_id'][0] == 1
    assert df['input_data_id'][0] == 3
    assert 'label_serialised' in df.columns


def test_get_all_completed_labels_when_specifying_dataset_id(refresh_db_once, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    df = sql_queries.get_all_completed_labels(engine, label_task_id=1, dataset_id=3)

    assert len(df) == 0
