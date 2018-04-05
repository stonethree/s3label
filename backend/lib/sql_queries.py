import pandas as pd


def count_total_images(label_task_id, engine):
    """
    Count number of total images (labeled + unlabeled) for a given label task

    :param label_task_id:
    :param engine: SQLAlchemy engine
    :return: total number of images for this label task
    """

    sql_query = """SELECT COUNT(*) FROM
        (
        SELECT dgl.dataset_id FROM dataset_group_lists dgl
        INNER JOIN label_tasks lt ON dgl.group_id = lt.dataset_group_id
        WHERE lt.label_task_id = {label_task_id}
        ) as t
        INNER JOIN input_data i ON t.dataset_id = i.dataset_id;""".format(label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query, engine)

    if len(df) > 0:
        num_images = df.values[0][0]
    else:
        num_images = 0

    return num_images


def get_all_images(label_task_id, engine):
    """
    Get list of all images (labeled + unlabeled) for a given label task

    :param label_task_id:
    :param engine: SQLAlchemy engine
    :return:
    """

    sql_query = """SELECT * FROM
        (
        SELECT dgl.dataset_id FROM dataset_group_lists dgl
        INNER JOIN label_tasks lt ON dgl.group_id = lt.dataset_group_id
        WHERE lt.label_task_id = {label_task_id}
        ) as t
        INNER JOIN input_data i ON t.dataset_id = i.dataset_id
        ORDER BY priority DESC;""".format(label_task_id=label_task_id)

    df = pd.read_sql_query(sql_query, engine)

    return df


def get_unlabeled_images(label_task_id, engine, num_images=None):
    """
    Get unlabeled images for a given task

    Can choose to get only the next one by setting num_images=1.

    :param label_task_id:
    :param engine: SQLAlchemy engine
    :param num_images: num images to get
    :return:
    """

    if num_images is None:
        num_images_str = ''
    else:
        num_images_str = 'LIMIT {}'.format(num_images)

    sql_query = """(SELECT i.* FROM
        (
        SELECT dgl.dataset_id FROM dataset_group_lists dgl
        INNER JOIN label_tasks lt ON dgl.group_id = lt.dataset_group_id
        WHERE lt.label_task_id = {label_task_id}
        ) as t 
        INNER JOIN input_data i ON t.dataset_id = i.dataset_id)
        EXCEPT 
        (SELECT i.* FROM input_data i INNER JOIN labels ON i.input_data_id = labels.input_data_id WHERE labels.in_progress)
        EXCEPT
        (SELECT ii.* FROM 
        (SELECT labels.input_data_id FROM labels 
        INNER JOIN label_history lh ON labels.label_id = lh.label_id
        WHERE labels.label_task_id = {label_task_id}) AS tt
        INNER JOIN input_data ii ON ii.input_data_id = tt.input_data_id)
        ORDER BY priority DESC {num_images_str};""".format(label_task_id=label_task_id, num_images_str=num_images_str)

    df = pd.read_sql_query(sql_query, engine)

    return df


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
