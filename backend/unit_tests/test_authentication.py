from backend.lib import user_authentication as ua


def test_get_user_id_from_token():
    token_identity = 'user_id=7'
    assert ua.get_user_id_from_token(token_identity) == 7


def test_user_can_view_data_if_data_created_by_user():
    assert ua.check_user_permitted(user_id=5, data_user_id=5, admin_ids=[1, 3, 6])


def test_user_can_view_data_if_user_is_an_admin_user():
    assert ua.check_user_permitted(user_id=6, data_user_id=7, admin_ids=[1, 3, 6])


def test_user_cannot_view_data_if_not_admin_and_did_not_create_data():
    assert not ua.check_user_permitted(user_id=5, data_user_id=7, admin_ids=[1, 3, 6])
