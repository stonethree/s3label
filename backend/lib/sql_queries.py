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


def get_all_datasets(engine):
    """
    Get list of all datasets

    :param engine: SQLAlchemy engine
    :return:
    """

    sql_query = """select * from datasets"""

    df = pd.read_sql_query(sql_query, engine)

    return df


def count_input_data_items_per_user_per_label_task(engine, label_task_id=None, user_id=None):
    """
    Count the number of labeled, unlabeled and in progress input data items per label task for the user

    :param engine: SQLAlchemy engine
    :param label_task_id:
    :param user_id:
    :return:
    """

    if label_task_id is not None and user_id is not None:
        where_clause = 'where label_task_id = %(label_task_id)s and user_id = %(user_id)s'
    elif label_task_id is not None:
        where_clause = 'where label_task_id = %(label_task_id)s'
    elif user_id is not None:
        where_clause = 'where user_id = %(user_id)s'
    else:
        where_clause = ''

    sql_query = """select * from item_counts {} order by user_id, label_task_id""".format(where_clause)

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id, 'user_id': user_id})

    return df


def get_next_unlabeled_input_data_item(engine, label_task_id, shuffle=True, n=1):
    """
    Get the highest priority input data item for the specified label task that has not yet been labeled and is not
    currently being labeled by another user

    :param engine:
    :param label_task_id:
    :param shuffle: if True, shuffle the data before sorting by priority
    :param n: number of items to return. If None, return all
    :return:
    """

    if shuffle:
        order_by = 'order by random(), priority desc'
    else:
        order_by = 'order by priority desc, input_data_id'

    if n is None:
        max_limit = ''
    else:
        max_limit = 'limit {}'.format(int(n))

    sql_query = """
        with unlabeled_items as (
            select * from labels_per_input_data_item
            where label_task_id = %(label_task_id)s and label_id isnull and not input_data_id isnull
        )
        select * from unlabeled_items
        {order_by}
        {max_limit}""".format(order_by=order_by, max_limit=max_limit)

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id})

    if len(df) > 0:
        return df
    else:
        return None


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

    fields = 'label_id, input_data_id, label_task_id, label_history_id, user_id, user_complete, needs_improvement, ' \
             'admin_complete, paid, include_in_test_set, user_comment, admin_comment, timestamp_edit'

    sql_query = """
    SELECT {fields} FROM latest_label_history WHERE user_id=%(user_id)s AND label_task_id=%(label_task_id)s 
    ORDER BY label_id DESC LIMIT {n}""".format(fields=fields, n=n)

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id})

    return df
    
    
def get_all_user_input_data_filtered(engine, user_id, label_task_id, label_filter):
    """
    Get the first input_data item that matches the filter.

    :param engine:
    :param user_id:
    :param label_task_id:
    :param label_filter: filter indicating user_complete or user_incomplete 
    :return:
    """

    # Apply the filter

    if label_filter == "filter_complete":
        complete = True
    else:
        complete = False

    fields = 'label_id, input_data_id, label_task_id, label_history_id, user_id, user_complete, needs_improvement, ' \
             'admin_complete, paid, include_in_test_set, user_comment, admin_comment, timestamp_edit'

    sql_query = """
    SELECT {fields} FROM latest_label_history a WHERE user_id=%(user_id)s AND label_task_id=%(label_task_id)s AND user_complete={complete}
    AND label_history_id > 0 ORDER BY input_data_id ASC""".format(fields=fields, complete=complete)

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id})

    return df
    

def get_first_user_input_data(engine, user_id, label_task_id, label_filter):
    """
    Get the first input_data item that matches the filter.

    :param engine:
    :param user_id:
    :param label_task_id:
    :param label_filter: filter indicating user_complete or user_incomplete 
    :return:
    """
    df = get_all_user_input_data_filtered(engine, user_id, label_task_id, label_filter)
    entry = df.iloc[0:1, :]
    
    return entry 


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
        
        
def get_preceding_user_data_item_filtered(engine, user_id, label_task_id, current_input_data_id, label_filter):
    """
    Get preceding input data that the user has viewed (whether they have actually labeled any of it or not)

    :param engine:
    :param user_id:
    :param label_task_id:
    :param current_input_data_id: current input data ID (we want to find the item before this in the list)
    :label_filter: the filter according
    :return:
    """

    # retrieve all data from database for that user and label task
    df = get_all_user_input_data_filtered(engine, user_id, label_task_id, label_filter)

    # here the list is in ascending order.  
    matching_indices = df.index[df['input_data_id'] <= current_input_data_id].tolist()

    if len(matching_indices) >= 1:
        idx = matching_indices[len(matching_indices)-1]
        return df.iloc[idx - 1:idx, :]
    else:
        return pd.DataFrame(columns=df.columns)


def get_next_user_data_item_filtered(engine, user_id, label_task_id, current_input_data_id, label_filter):
    """
    Get next input data that the user has viewed (whether they have actually labeled any of it or not)

    :param engine:
    :param user_id:
    :param label_task_id:
    :param current_input_data_id: current input data ID (we want to find the item before this in the list)
    :return:
    """

    # retrieve all data from database for that user and label task
    df = get_all_user_input_data_filtered(engine, user_id, label_task_id, label_filter)

    # get the next input data item in the list (the list is in descending order of label ID, so we get the next item)
    matching_indices = df.index[df['input_data_id'] >= current_input_data_id].tolist()
        
    if len(matching_indices) >= 1:
        idx = matching_indices[0]
        return df.iloc[idx + 1:idx + 2, :]
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


def get_example_image_path(engine, example_labeling_id):
    """
    Get the path to the example labeled image item on disk

    :param engine: SQLAlchemy engine
    :param example_labeling_id: ID of the example label image
    :return: path to the data item
    """

    sql_query = 'SELECT image_path FROM example_labeling ' \
                'WHERE example_labeling_id=%(example_labeling_id)s'

    df = pd.read_sql_query(sql_query, engine, params={'example_labeling_id': example_labeling_id})

    if len(df) > 0:
        return df.values[0][0]
    else:
        return None


def get_label_tasks(engine, user_id=None):
    """
    Get list of available label tasks

    :param engine: SQLAlchemy engine
    :param user_id: (optional) filter label tasks by the specified user ID: only show label tasks that have been
    labeled by that user
    :return: DataFrame containing label tasks
    """

    if user_id is None:
        sql_query = 'SELECT * FROM label_tasks'

        df = pd.read_sql_query(sql_query, engine)
    else:
        sql_query = """select label_tasks.* from users_label_tasks
            inner join label_tasks using (label_task_id)
            where user_id = :user_id
            order by label_task_id"""

        sql_query_2 = text(sql_query).bindparams(user_id=user_id)

        df = pd.read_sql_query(sql_query_2, engine)

        # drop the "user_id" column
        # df.drop(labels=['user_id'], axis=1, inplace=True)

    if len(df) > 0:
        return df
    else:
        return None


def get_label_task(engine, label_task_id):
    """
    Get a particular label tasks

    :param engine: SQLAlchemy engine
    :param label_task_id:
    :return: DataFrame containing label tasks
    """

    sql_query = 'SELECT * FROM label_tasks WHERE label_task_id = :label_task_id'

    sql_query_2 = text(sql_query).bindparams(label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query_2, engine)

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

    sql_query = """select *, label_serialised::text label_serialised_text from latest_label_history
        where user_id = %(user_id)s and label_task_id = %(label_task_id)s and input_data_id = %(input_data_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'input_data_id': input_data_id})

    # use the text

    df['label_serialised'] = df['label_serialised_text']
    df.drop('label_serialised_text', axis=1, inplace=True)

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
        where user_id = %(user_id)s and label_task_id = %(label_task_id)s and input_data_id = %(input_data_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'input_data_id': input_data_id})

    if len(df) > 0:
        return int(df.values[0][0])
    else:
        return None


def get_label(engine, user_id, label_task_id, input_data_id):
    """
    Get label for this input data item and label task

    :param engine:
    :param user_id:
    :param label_task_id:
    :param input_data_id:
    :return:
    """

    sql_query = """select * from labels 
        where user_id = %(user_id)s and label_task_id = %(label_task_id)s and input_data_id = %(input_data_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'user_id': user_id,
                                                      'label_task_id': label_task_id,
                                                      'input_data_id': input_data_id})

    if len(df) > 0:
        return df
    else:
        return None


def get_label_by_id(engine, label_id):
    """
    Get label corresponding to this label_id

    :param engine:
    :param label_id:
    :return:
    """

    sql_query = """select * from labels where label_id = %(label_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'label_id': label_id})

    if len(df) > 0:
        return df
    else:
        return None


def get_all_completed_labels(engine, label_task_id, dataset_id=None, label_status="admin_complete"):
    """
    Get latest label history entries for all completed (approved) labels

    :param engine:
    :param label_task_id:
    :param dataset_id: optionally specify a dataset ID to only return labels for this dataset
    :param label_status: specify whether to only get images that have "admin_complete" or "user_complete" set
    :return:
    """

    if dataset_id is None:
        dataset_clause = ''
    else:
        dataset_clause = 'where dataset_id=%(dataset_id)s'

    sql_query = """
    with t as (
        select *, label_serialised::text label_serialised_text from latest_label_history
            where label_task_id = %(label_task_id)s and {label_status}
    )
    select t.*, dataset_id, data_path from t inner join input_data using (input_data_id) {dataset_clause}
    """.format(dataset_clause=dataset_clause, label_status=label_status)

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id,
                                                      'dataset_id': dataset_id})

    # use the text

    df['label_serialised'] = df['label_serialised_text']
    df.drop('label_serialised_text', axis=1, inplace=True)

    return df


def get_example_labelings(engine, label_task_id):
    """
    Get example labelings for this label task

    :param engine:
    :param label_task_id:
    :return:
    """

    sql_query = """select example_labeling_id, title, description from example_labeling 
        where label_task_id = %(label_task_id)s"""

    df = pd.read_sql_query(sql_query, engine, params={'label_task_id': label_task_id})

    if len(df) > 0:
        return df
    else:
        return None


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


def update_label_status(engine, label_id, user_complete=None, needs_improvement=None, admin_complete=None, paid=None,
                        user_comment=None, admin_comment=None):
    """
    Update particular status fields of a label

    :param engine:
    :param label_id: ID of label to be modified
    :param user_complete:
    :param needs_improvement:
    :param admin_complete:
    :param paid:
    :param user_comment:
    :param admin_comment:
    :return:
    """

    update_fields = []

    if user_complete is not None:
        if user_complete:
            update_fields.append('user_complete=true')
        else:
            update_fields.append('user_complete=false')

    if needs_improvement is not None:
        if needs_improvement:
            update_fields.append('needs_improvement=true')
        else:
            update_fields.append('needs_improvement=false')

    if admin_complete is not None:
        if admin_complete:
            update_fields.append('admin_complete=true')
        else:
            update_fields.append('admin_complete=false')

    if paid is not None:
        if paid:
            update_fields.append('paid=true')
        else:
            update_fields.append('paid=false')

    if user_comment is not None:
        update_fields.append('user_comment=:user_comment')

    if admin_comment is not None:
        update_fields.append('admin_comment=:admin_comment')

    if len(update_fields) > 0:
        sql_query_2 = """
            UPDATE labels SET {update_fields} WHERE label_id = :label_id RETURNING label_id
            """.format(update_fields=','.join(update_fields))

        # execute the query

        sql_query_3 = text(sql_query_2)

        result = engine.execute(sql_query_3.execution_options(autocommit=True),
                                label_id=int(label_id),
                                user_comment=user_comment,
                                admin_comment=admin_comment
                                )

        # read the label ID from the returned result

        label_id_returned = [r for r in result][0][0]

        return label_id_returned
    else:
        return None
