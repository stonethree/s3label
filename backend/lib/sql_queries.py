import pandas as pd


def get_all_images(engine, label_task_id):
    """
    Get list of all images (labeled + unlabeled) for a given label task

    :param engine: SQLAlchemy engine
    :param label_task_id:
    :return:
    """

    sql_query = """select distinct on (input_data_id) * from
        (
            select input_data_id, dataset_group_id, dataset_id from input_data_per_label_task
            where label_task_id = {label_task_id}
        ) as all_images""".format(label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query, engine)

    return df


def get_next_unlabeled_image(engine, label_task_id, user_id):
    """
    Get the highest priority input data item for the specified label task that has not yet been labeled and is not
    currently being labeled by another user

    :param engine:
    :param label_task_id:
    :param user_id:
    :return:
    """

    sql_query = """select * from latest_label_history_per_input_item
        where not in_progress and label_serialised isnull and user_id = {user_id} and label_task_id = {label_task_id}
        order by priority desc
        limit 1""".format(user_id=user_id, label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query, engine)

    return df


def get_recent_labeled_input_data(engine, user_id, label_task_id, input_data_id, n):
    """
    Get most recently labeled input data

    This allows user to skip back through previously labeled data

    :param engine:
    :param user_id:
    :param label_task_id:
    :param input_data_id: ID of current input data item
    :param n: number of items to return
    :return:
    """

    pass


def get_input_data_path(input_data_id, engine):
    """
    Get the path to the data item on disk

    :param input_data_id: ID of the data item
    :param engine: SQLAlchemy engine
    :return: path to the data item
    """

    sql_query = 'SELECT image_path FROM input_data ' \
                'WHERE input_data_id={input_data_id}'.format(input_data_id=input_data_id)

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


def get_label_tasks(engine):
    """
    Get list of available label tasks

    :param engine: SQLAlchemy engine
    :return: DataFrame containing label tasks
    """

    sql_query = 'SELECT * FROM label_tasks'

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        return df
    else:
        return None


def get_latest_label(engine, user_id, label_task_id, input_data_id):
    """
    Get latest label history entry for this input data item

    :param engine:
    :param user_id:
    :param label_task_id:
    :param input_data_id:
    :return:
    """

    sql_query = """select * from latest_label_history
        where user_id = {user_id} and label_task_id = {label_task_id} and input_data_id = {input_data_id}"""\
            .format(user_id=user_id,
                    label_task_id=label_task_id,
                    input_data_id=input_data_id)

    df = pd.read_sql_query(sql_query, engine)

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


def create_new_label(engine, input_data_id, user_id, label_task_id, serialised_label):
    """

    :param engine:
    :param input_data_id:
    :param user_id:
    :param label_task_id:
    :param serialised_label:
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
