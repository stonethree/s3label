import pandas as pd
from sqlalchemy.sql import text


def get_user_id(engine, email, password):
    """
    Get user ID associated with the given user's email and password

    :param engine: SQLAlchemy engine
    :param email: email address of user
    :param password: user's password
    :return: info about user
    """

    sql_query = """select user_id from users where email = :email and password = :password limit 1"""

    # execute the query

    sql_query_2 = text(sql_query).bindparams(email=email, password=password)

    df = pd.read_sql_query(sql_query_2, engine)

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


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
            where label_task_id = %(label_task_id)s
        ) as all_input_data_items"""

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id})

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
            and label_task_id = %(label_task_id)s
            order by priority desc
            limit 1"""

    # TODO: should optionally shuffle label data, then sort by priority

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id})

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


def get_recent_labeled_input_data(engine, user_id, label_task_id, input_data_id, n, include_current_input_data):
    """
    Get most recently labeled input data

    This allows user to skip back through previously labeled data

    :param engine:
    :param user_id:
    :param label_task_id:
    :param input_data_id: ID of current input data item
    :param n: number of items to return (set to None if no limit)
    :param include_current_input_data: if True, includes the input data item whose ID is specified
    :return:
    """

    # choose whether to include up to and including, or just up to, the specified input data ID

    if include_current_input_data:
        include_mode = 2
    else:
        include_mode = 1

    # choose whether to return some or all of the items

    if n is None:
        n = 'ALL'
    else:
        n = int(n)

    sql_query = """
    WITH tmp_table AS (
        SELECT *, (input_data_id=%(input_data_id)s)::int AS last_input_data_item FROM latest_label_history_per_input_item
        WHERE NOT in_progress AND NOT label_serialised ISNULL
        AND user_id = %(user_id)s AND label_task_id = %(label_task_id)s
    ),
    tmp_table_2 AS (
        SELECT *, SUM(last_input_data_item) OVER (order by label_id) AS summed FROM tmp_table
    ),
    tmp_table_3 AS (
        SELECT *, SUM(summed) OVER (order by label_id) AS summed_2 FROM tmp_table_2
    ),
    tmp_table_4 AS (
        SELECT * FROM tmp_table_3 WHERE summed_2 <= %(include_mode)s ORDER BY label_id DESC LIMIT {n}
    )
    SELECT * FROM tmp_table_4 ORDER BY label_id ASC""".format(n=n)

    df = pd.read_sql_query(sql_query, engine, params={'input_data_id': input_data_id,
                                                      'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'include_mode': include_mode})

    return df


def get_all_user_input_data(engine, user_id, label_task_id, n):
    """
    Get all input data that the user has viewed (whether they have actually labeled any of it or not)

    :param engine:
    :param user_id:
    :param label_task_id:
    :param n: number of items to return (set to None if no limit)
    :return:
    """

    # choose whether to return some or all of the items

    if n is None:
        n = 'ALL'
    else:
        n = int(n)

    fields = 'label_id, input_data_id, label_task_id, user_id, user_complete, admin_complete, paid, user_comment, ' \
             'admin_comment'

    sql_query = """
    SELECT {fields} FROM latest_label_history WHERE user_id=%(user_id)s AND label_task_id=%(label_task_id)s 
    ORDER BY label_id DESC LIMIT {n}""".format(fields=fields, n=n)

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id})

    return df


def get_preceding_user_data_item(engine, user_id, label_task_id, current_input_data_id):
    """
    Get preceding input data that the user has viewed (whether they have actually labeled any of it or not)

    :param engine:
    :param user_id:
    :param label_task_id:
    :param current_input_data_id: current input data ID (we want to find the item before this in the list)
    :return:
    """

    # retrieve all data from database for that user and label task

    df = get_all_user_input_data(engine, user_id, label_task_id, n=None)

    # get the next input data item in the list (the list is in descending order of label ID, so we get the next item)

    matching_indices = df.index[df['input_data_id'] == current_input_data_id].tolist()

    if len(matching_indices) >= 1:
        idx = matching_indices[0]
        return df.iloc[idx + 1:idx + 2, :]
    else:
        return pd.DataFrame(columns=df.columns)


def get_next_user_data_item(engine, user_id, label_task_id, current_input_data_id):
    """
    Get next input data that the user has viewed (whether they have actually labeled any of it or not)

    :param engine:
    :param user_id:
    :param label_task_id:
    :param current_input_data_id: current input data ID (we want to find the item before this in the list)
    :return:
    """

    # retrieve all data from database for that user and label task

    df = get_all_user_input_data(engine, user_id, label_task_id, n=None)

    # get the next input data item in the list (the list is in descending order of label ID, so we get the next item)

    matching_indices = df.index[df['input_data_id'] == current_input_data_id].tolist()

    if len(matching_indices) >= 1:
        idx = matching_indices[0]
        return df.iloc[idx - 1:idx, :]
    else:
        return pd.DataFrame(columns=df.columns)


def get_input_data_path(engine, input_data_id):
    """
    Get the path to the data item on disk

    :param engine: SQLAlchemy engine
    :param input_data_id: ID of the data item
    :return: path to the data item
    """

    sql_query = 'SELECT data_path FROM input_data ' \
                'WHERE input_data_id=%(input_data_id)s'

    df = pd.read_sql_query(sql_query, engine, params={'input_data_id': input_data_id})

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
        where user_id = %(user_id)s and label_task_id = %(label_task_id)s and input_data_id = %(input_data_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'input_data_id': input_data_id})

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
        where user_id = %(user_id)s and %(label_task_id)s = %(label_task_id)s and input_data_id = %(input_data_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'input_data_id': input_data_id})

    if len(df) > 0:
        return int(df.values[0][0])
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
                UPDATE labels SET in_progress = false WHERE user_id = :user_id
            )
            INSERT INTO labels (input_data_id, label_task_id, user_id, in_progress) 
            VALUES (:input_data_id, :label_task_id, :user_id, true) RETURNING label_id;
            """

        # execute the query

        sql_query_3 = text(sql_query_2)

        result = engine.execute(sql_query_3.execution_options(autocommit=True),
                                input_data_id=int(input_data_id),
                                label_task_id=int(label_task_id),
                                user_id=int(user_id)
                                )
    else:
        # update in_progress field of existing label

        sql_query_2 = """
            WITH tmp_table AS (
                UPDATE labels SET in_progress = false WHERE user_id = :user_id
            )
            UPDATE labels SET in_progress = true WHERE label_id = :label_id RETURNING label_id;
            """

        # execute the query

        sql_query_3 = text(sql_query_2)

        result = engine.execute(sql_query_3.execution_options(autocommit=True),
                                user_id=int(user_id),
                                label_id=int(label_id)
                                )

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

    sql_query = """INSERT INTO label_history (label_id, label_serialised) VALUES (:label_id, :serialised_label)  
        RETURNING label_history_id"""

    sql_query_2 = text(sql_query)

    result = engine.execute(sql_query_2.execution_options(autocommit=True),
                            label_id=int(label_id),
                            serialised_label=serialised_label
                            )

    label_history_id = int([r[0] for r in result][0])

    return label_history_id


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
