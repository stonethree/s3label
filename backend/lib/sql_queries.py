import pandas as pd
from sqlalchemy.sql import text


# TODO: convert user_code to user_id on the backend, so that user does not need to know user_id
# TODO: protect against SQL injection


def get_all_input_data_items(engine, label_task_id):
    """
    Get list of all input data items (labeled + unlabeled) for a given label task

    :param engine: SQLAlchemy engine
    :param label_task_id:
    :return:
    """

    sql_query = """select distinct on (input_data_id) * from
        (
            select input_data_id, dataset_group_id, dataset_id from input_data_per_label_task
            where label_task_id = {label_task_id}
        ) as all_input_data_items""".format(label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query, engine)

    return df


def get_next_unlabeled_input_data_item(engine, label_task_id):
    """
    Get the highest priority input data item for the specified label task that has not yet been labeled and is not
    currently being labeled by another user

    :param engine:
    :param label_task_id:
    :return:
    """

    sql_query = """select * from latest_label_history_per_input_item
            where (not in_progress or in_progress isnull) and label_serialised isnull
            and label_task_id = {label_task_id}
            order by priority desc
            limit 1""".format(label_task_id=label_task_id)

    # TODO: should optionally shuffle label data, then sort by priority

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


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


def get_input_data_path(engine, input_data_id):
    """
    Get the path to the data item on disk

    :param engine: SQLAlchemy engine
    :param input_data_id: ID of the data item
    :return: path to the data item
    """

    sql_query = 'SELECT data_path FROM input_data ' \
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


def get_label_id(engine, user_id, label_task_id, input_data_id):
    """
    Get label ID for this input data item and label task

    :param engine:
    :param user_id:
    :param label_task_id:
    :param input_data_id:
    :return:
    """

    sql_query = """select label_id from labels 
        where user_id = {user_id} and label_task_id = {label_task_id} and input_data_id = {input_data_id}""" \
            .format(user_id=user_id,
                    label_task_id=label_task_id,
                    input_data_id=input_data_id)

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


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


def create_new_label(engine, input_data_id, label_task_id, user_id):
    """
    Get the highest priority input data item for the specified label task that has not yet been labeled and is not
    currently being labeled by another user

    :param engine:
    :param input_data_id: item to be labeled
    :param label_task_id:
    :param user_id:
    :return:
    """

    # check if label exists

    label_id = get_label_id(engine, user_id, label_task_id, input_data_id)

    if label_id is None:
        # create label for this input data item and set in_progress = true

        sql_query_2 = """
            WITH tmp_table AS (
                UPDATE labels SET in_progress = false WHERE user_id = 4
            )
            INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) 
            VALUES ({input_data_id}, {label_task_id}, {user_id}, true) RETURNING label_id;
            """.format(input_data_id=input_data_id,
                       label_task_id=label_task_id,
                       user_id=user_id)
    else:
        # update in_progress field of existing label

        sql_query_2 = """
            WITH tmp_table AS (
                UPDATE labels SET in_progress = false WHERE user_id = 4
            )
            UPDATE labels SET in_progress = true WHERE label_id = {label_id} RETURNING label_id;
            """.format(user_id=user_id, label_id=label_id)

    # execute the query

    sql_query_3 = text(sql_query_2)

    result = engine.execute(sql_query_3.execution_options(autocommit=True))

    # read the label ID from the returned result

    label_id_returned = [r for r in result][0][0]

    return label_id_returned


def create_new_label_history(engine, label_id, serialised_label):
    """
    Add a new label history entry for the specified input data item

    :param engine:
    :param label_id:
    :param serialised_label: serialised JSON string representing a ground truth label for the input data item
    :return:
    """

    sql_query = """INSERT INTO label_history (label_id, label_serialised) VALUES ({label_id}, '{serialised_label}')  
        RETURNING label_history_id""" \
        .format(label_id=label_id,
                serialised_label=serialised_label)

    sql_query_2 = text(sql_query)

    result = engine.execute(sql_query_2.execution_options(autocommit=True))

    label_history_pks = [r[0] for r in result]

    return label_history_pks


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
