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


def create_new_input_data_item(engine, input_data_path, dataset_id, sha1_hash):
    """

    :param engine:
    :param input_data_path:
    :param dataset_id:
    :param sha1_hash: SHA-1 hash of the input data item
    :return:
    """

    sql_query = """
                INSERT INTO input_data (dataset_id, data_path, sha1_hash) VALUES (:dataset_id, :data_path, :sha1_hash) 
                RETURNING input_data_id;
                """

    # execute the query

    sql_query = text(sql_query)

    result = engine.execute(sql_query.execution_options(autocommit=True),
                            dataset_id=int(dataset_id),
                            data_path=input_data_path,
                            sha1_hash=sha1_hash
                            )

    # read the label ID from the returned result

    input_data_id = [r for r in result][0][0]

    return input_data_id


def create_new_dataset_group(engine, dataset_ids, description):
    """
    Group the specified datasets together

    :param engine:
    :param dataset_ids:
    :param description:
    :return:
    """

    pass


def get_missing_input_data(engine):
    """
    Get list of input data items that are missing from disk

    :return:
    """

    sql_query = """select data_path from input_data"""

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        return df
    else:
        return None
