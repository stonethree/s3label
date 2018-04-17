def get_user_id_from_token(jwt_identity):
    """
    Extract the user ID from a JSON web token (after the token has been decrypted)

    :param jwt_identity: string containing user ID in the form: 'user_id=<user_id>'
    :return: user ID
    """

    return int(jwt_identity.split('=')[1])


def check_user_permitted(user_id, data_user_id, admin_ids):
    """
    Check the data is permitted to be viewed or edited by the user.

    Admin users can view or edit any data

    :param user_id: ID of user requesting access to the data
    :param data_user_id: user ID to which the data belongs
    :param admin_ids: list of IDs of the admin users
    :return:
    """

    if user_id in admin_ids or user_id == data_user_id:
        return True
    else:
        return False
