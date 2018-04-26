import pandas as pd
from sqlalchemy.sql import text


def is_user_an_admin(engine, user_id):
    """
    Check if user ID corresponds to an admin user

    :param engine: SQLAlchemy engine
    :param user_id: user ID
    :return:
    """

    sql_query = """select user_id, is_admin from users where user_id = :user_id"""

    sql_query_2 = text(sql_query).bindparams(user_id=user_id)

    df = pd.read_sql_query(sql_query_2, engine)

    if len(df) == 1:
        return df['is_admin'].values[0]
    else:
        return None


def get_users(engine):
    """
    Get list of all users

    :param engine: SQLAlchemy engine
    :return:
    """

    sql_query = """select user_id, first_name, last_name, email, organisation, note, is_admin from users"""

    df = pd.read_sql_query(sql_query, engine)

    return df


def get_label_task_ids_for_a_user(engine, user_id):
    """
    Get list of all label tasks that a user has labeled images for

    :param engine: SQLAlchemy engine
    :param user_id: User ID to check label tasks for
    :return:
    """

    sql_query = """select distinct label_task_id from labels where user_id = :user_id"""

    sql_query_2 = text(sql_query).bindparams(user_id=user_id)

    df = pd.read_sql_query(sql_query_2, engine)

    return df


def get_labeled_data_for_user_and_task(engine, user_id, label_task_id):
    """
    Get list of all items that user has labeled for a specified label task

    :param engine: SQLAlchemy engine
    :param user_id: User ID to check labeled data for
    :param label_task_id:
    :return:
    """

    sql_query = """select * from latest_label_history_per_input_item 
        where user_id = :user_id and label_task_id = :label_task_id and not label_serialised isnull 
        order by label_id desc"""

    sql_query_2 = text(sql_query).bindparams(user_id=user_id, label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query_2, engine)

    return df


def create_new_dataset(engine, site, sensor, description):
    """
    Create a new dataset

    :param engine:
    :param site:
    :param sensor:
    :param description:
    :return:
    """

    pass


def create_new_input_data_item(engine, input_data_path, dataset_id):
    """

    :param engine:
    :param input_data_path:
    :param dataset_id:
    :return:
    """

    pass


def create_new_dataset_group(engine, dataset_ids, description):
    """
    Group the specified datasets together

    :param engine:
    :param dataset_ids:
    :param description:
    :return:
    """

    pass


def delete_dataset_group(engine, dataset_group_id):
    """
    Delete the specified dataset group

    :param engine:
    :param dataset_group_id:
    :return:
    """

    pass


def delete_label_task(engine, label_task_id):
    """
    Delete the specified label task

    :param engine:
    :param label_task_id:
    :return:
    """

    pass
