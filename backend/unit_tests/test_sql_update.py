from backend.lib import sql_queries


def test_update_label_status_user_complete(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, user_complete=True)

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert df['user_complete'][0]
    assert not df['needs_improvement'][0]
    assert not df['admin_complete'][0]
    assert not df['paid'][0]


def test_update_label_status_needs_improvement(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, needs_improvement=True)

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert not df['user_complete'][0]
    assert df['needs_improvement'][0]
    assert not df['admin_complete'][0]
    assert not df['paid'][0]


def test_update_label_status_admin_complete(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, admin_complete=True)

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert not df['user_complete'][0]
    assert not df['needs_improvement'][0]
    assert df['admin_complete'][0]
    assert not df['paid'][0]


def test_update_label_status_paid(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, paid=True)

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert not df['user_complete'][0]
    assert not df['needs_improvement'][0]
    assert not df['admin_complete'][0]
    assert df['paid'][0]


def test_update_label_status_admin_complete_and_paid(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, admin_complete=True, paid=True)

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert not df['user_complete'][0]
    assert not df['needs_improvement'][0]
    assert df['admin_complete'][0]
    assert df['paid'][0]


def test_update_label_status_user_comment(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, user_comment='abcdef')

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert df['user_comment'][0] == 'abcdef'


def test_update_label_status_admin_comment(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3, admin_comment='abcdefg')

    assert label_id == 3

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert df['admin_comment'][0] == 'abcdefg'


def test_update_label_status_do_nothing_if_no_statuses_specified(refresh_db_every_time, db_connection_sqlalchemy):
    engine = db_connection_sqlalchemy
    label_id = sql_queries.update_label_status(engine, label_id=3)

    assert label_id is None

    df = sql_queries.get_label(engine, user_id=1, label_task_id=1, input_data_id=3)

    assert not df['user_complete'][0]
    assert not df['needs_improvement'][0]
    assert not df['admin_complete'][0]
    assert not df['paid'][0]
