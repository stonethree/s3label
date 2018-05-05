from flask import jsonify, request, send_file, make_response, current_app, Blueprint
import flask_jwt_extended as fje
import json
import os

from backend.lib import sql_queries, sql_queries_admin, user_authentication as ua
from backend.lib import data_upload as du

# create a "blueprint" for the endpoints in this file
ebp = Blueprint('endpoints', __name__)

# ---------------  GET requests ---------------


@ebp.route('/')
def homepage():
    return json.dumps({'message': 'You have found the S3 Label image server!'}), 200


@ebp.route('/image_labeler/api/v1.0/label_tasks', methods=['GET'])
@fje.jwt_required
def get_label_tasks():
    engine = current_app.config['engine']
    df_label_tasks = sql_queries.get_label_tasks(engine)

    if df_label_tasks is not None:
        resp = make_response(df_label_tasks.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No label tasks found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/label_tasks/<int:label_task_id>', methods=['GET'])
@fje.jwt_required
def get_label_task(label_task_id):
    engine = current_app.config['engine']
    df_label_task = sql_queries.get_label_task(engine, label_task_id)

    if df_label_task is not None:
        resp = make_response(df_label_task.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No label task found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/image_paths', methods=['GET'])
@fje.jwt_required
def get_image_paths_in_folder():
    engine = current_app.config['engine']

    # check that the user has permission to get the requested data: admin users can get any user's data, but an
    # ordinary user can only get their own data

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

    if is_admin is None or not is_admin:
        resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
        resp.mimetype = "application/javascript"
        return resp

    folder_path = request.args.get('folder_path', None)
    recursive = request.args.get('recursive', None)

    if recursive == 'True' or recursive == 'true':
        recursive = True
    else:
        recursive = False

    if folder_path is None:
        resp = make_response(jsonify(error='Need to specify a folder path.'), 400)
        resp.mimetype = "application/javascript"
        return resp
    elif not os.path.exists(folder_path):
        resp = make_response(jsonify(error='Need to specify a folder path that exists.'), 400)
        resp.mimetype = "application/javascript"
        return resp

    im_paths = du.get_images_in_folder(folder_path, recursive)

    resp = make_response(jsonify(image_paths=im_paths), 200)
    resp.mimetype = "application/javascript"
    return resp


@ebp.route('/image_labeler/api/v1.0/input_images/<int:input_image_id>', methods=['GET'])
# @fje.jwt_required
def get_image(input_image_id):
    engine = current_app.config['engine']
    image_folder = current_app.config['image_folder']
    im_path = sql_queries.get_input_data_path(engine, input_image_id)

    im_path = os.path.abspath(os.path.join(image_folder, im_path))

    if im_path is not None and os.path.exists(im_path):
        return send_file(im_path)
    else:
        print('Could not find image: ', im_path)
        resp = make_response(jsonify(error='Input data item not found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/labeled_data/label_tasks/<int:label_task_id>', methods=['GET'])
@fje.jwt_required
def get_next_or_preceding_input_data_item(label_task_id):
    """
    Get next or preceding data item that the user has labeled or viewed (ordered by label ID, i.e. when the label was
    initially created).

    The current input data ID is given, then the item following or preceding it (in order of label ID) is returned.

    :param label_task_id:
    :return:
    """

    engine = current_app.config['engine']

    # check that the user has permission to get the requested data: admin users can get any user's data, but an
    # ordinary user can only get their own data

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # get the ID of the input data item to end the selection at

    current_input_data_id = request.args.get('current_input_data_id', None)
    action = request.args.get('action', None)

    if action is None or action not in ['next', 'previous']:
        resp = make_response(jsonify(error='Must specify whether to return next data item (action="next") or previous '
                                           'data item (action="previous")'), 400)
        resp.mimetype = "application/javascript"
        return resp

    try:
        current_input_data_id = int(current_input_data_id)
    except (ValueError, TypeError):
        resp = make_response(jsonify(error='current_input_data_id must be an integer'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if current_input_data_id is None:
        resp = make_response(jsonify(error='Need to specify current input data ID'), 400)
        resp.mimetype = "application/javascript"
        return resp

    try:
        if action == 'previous':
            df_input_data = sql_queries.get_preceding_user_data_item(engine,
                                                                     user_id=user_id_from_auth,
                                                                     label_task_id=label_task_id,
                                                                     current_input_data_id=current_input_data_id)
        else:
            df_input_data = sql_queries.get_next_user_data_item(engine,
                                                                user_id=user_id_from_auth,
                                                                label_task_id=label_task_id,
                                                                current_input_data_id=current_input_data_id)

        resp = make_response(df_input_data.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    except Exception:
        resp = make_response(jsonify(error='No labeled data found for this user and/or label task'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/item_counts', methods=['GET'])
@fje.jwt_required
def get_labeled_and_unlabeled_item_counts():
    """
    Count the number of labeled and unlabeled input data items per user per label task

    Requires admin privileges if viewing all users' data. Normal users can view their own data.

    :return:
    """

    engine = current_app.config['engine']

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # get optional URL query parameters

    user_id = request.args.get('user_id', None)
    label_task_id = request.args.get('label_task_id', None)

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        user_id = None

    try:
        label_task_id = int(label_task_id)
    except (ValueError, TypeError):
        label_task_id = None

    # check if user is an admin user

    is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

    if is_admin is None or not is_admin:
        # only allow non-admin user to view their own data
        if user_id is None or user_id != user_id_from_auth:
            resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
            resp.mimetype = "application/javascript"
            return resp

    df_counts = sql_queries.count_input_data_items_per_user_per_label_task(engine, label_task_id, user_id)

    if df_counts is not None:
        resp = make_response(df_counts.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No users found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/all_data/label_tasks/<int:label_task_id>/users/<user_id>', methods=['GET'])
@fje.jwt_required
def get_all_user_input_data(label_task_id, user_id):
    """
    Get all the IDs of the input data that the user has viewed (labeled or not)

    :param label_task_id:
    :param user_id:
    :return:
    """

    engine = current_app.config['engine']

    # check that the user has permission to get the requested data: admin users can get any user's data, but an
    # ordinary user can only get their own data

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # get user ID specified

    try:
        user_id = int(user_id)
    except ValueError:
        if user_id == 'own':
            user_id = user_id_from_auth
        else:
            resp = make_response(jsonify(error='Must either specify ".../user_id/own" or ".../user_id/<user_id>"'), 405)
            resp.mimetype = "application/javascript"
            return resp

    if user_id != user_id_from_auth:
        is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

        if is_admin is None or not is_admin:
            resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
            resp.mimetype = "application/javascript"
            return resp

    # choose how many images to request

    num_labeled_images = request.args.get('num_labeled_images', None)

    print('num_labeled_images:', num_labeled_images)

    try:
        df_input_data = sql_queries.get_all_user_input_data(engine,
                                                            user_id=user_id,
                                                            label_task_id=label_task_id,
                                                            n=num_labeled_images)

        resp = make_response(df_input_data.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    except Exception:
        resp = make_response(jsonify(error='No input data found for this user and/or label task'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/labels/input_data/<int:input_data_id>/label_tasks/<int:label_task_id>', methods=['GET'])
@fje.jwt_required
def get_latest_label_history(input_data_id, label_task_id):
    """
    Get the latest label history item for a particular user/label task/input data item combination

    :param input_data_id:
    :param label_task_id:
    :return:
    """

    engine = current_app.config['engine']

    user_identity = fje.get_jwt_identity()
    user_id = ua.get_user_id_from_token(user_identity)

    df_latest_label = sql_queries.get_latest_label(engine, user_id, label_task_id, input_data_id)

    if df_latest_label is not None:
        resp = make_response(df_latest_label.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No label found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/label_ids/label_tasks/<int:label_task_id>/input_data/<int:input_data_id>/user/<int:user_id>',
           methods=['GET'])
@fje.jwt_required
def get_label_id(user_id, label_task_id, input_data_id):
    """
    Store the label for a particular label task, user and input data item

    :param user_id: ID of user
    :param label_task_id: ID of the label task that we want to retrieve an image for
    :param input_data_id: ID of the input data item that has been labeled
    :return:
    """

    engine = current_app.config['engine']

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    if user_id != user_id_from_auth:
        is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

        if is_admin is None or not is_admin:
            resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
            resp.mimetype = "application/javascript"
            return resp

    try:
        # find the label that the serialised label corresponds to

        label_id = sql_queries.get_label_id(engine,
                                            user_id=user_id,
                                            label_task_id=label_task_id,
                                            input_data_id=input_data_id)

        if label_id is None:
            resp = make_response(jsonify(error='Could not find label ID'), 404)
            resp.mimetype = "application/javascript"
            return resp
        else:
            resp = make_response(jsonify(label_id=label_id), 200)
            resp.mimetype = "application/javascript"
            return resp
    except Exception:
        resp = make_response(jsonify(error='Bad request'), 400)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/labels/<int:label_id>',
           methods=['GET'])
@fje.jwt_required
def get_label(label_id):
    """
    Get the label

    :param label_id: ID of label
    :return:
    """

    engine = current_app.config['engine']

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    try:
        df_labels = sql_queries.get_label_by_id(engine, label_id)

        if df_labels is None:
            resp = make_response(jsonify(error='Could not find label'), 404)
            resp.mimetype = "application/javascript"
            return resp
        else:
            # get the first label (which should be the only one)
            if len(df_labels) == 1:
                df_label = df_labels.iloc[0, :]
            else:
                raise ValueError('Expected single label to be returned')

            is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

            if df_label['user_id'] == user_id_from_auth or is_admin:
                resp = make_response(df_label.to_json(), 200)
                resp.mimetype = "application/javascript"
                return resp
            else:
                resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
                resp.mimetype = "application/javascript"
                return resp
    except Exception:
        resp = make_response(jsonify(error='Bad request'), 400)
        resp.mimetype = "application/javascript"
        return resp


# ------------- ADMIN get requests ---------------


@ebp.route('/image_labeler/api/v1.0/users', methods=['GET'])
@fje.jwt_required
def get_all_users():
    """
    Get list of users and their details

    Requires admin privileges

    :return:
    """

    engine = current_app.config['engine']

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # check if user is an admin user

    is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

    if is_admin is None or not is_admin:
        resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
        resp.mimetype = "application/javascript"
        return resp

    df_users = sql_queries_admin.get_users(engine)

    if df_users is not None:
        resp = make_response(df_users.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No users found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/label_tasks/users/<int:user_id>', methods=['GET'])
@fje.jwt_required
def get_label_tasks_for_user(user_id):
    """
    Get list of label tasks that the user has already labeled data for

    Requires admin privileges

    :param user_id: user ID of the user to get the tasks for
    :return:
    """

    engine = current_app.config['engine']

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # check if user is an admin user

    if user_id != user_id_from_auth:
        is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

        if is_admin is None or not is_admin:
            resp = make_response(jsonify(error='Not permitted to view this content. Must be an admin user.'), 403)
            resp.mimetype = "application/javascript"
            return resp

    df_label_tasks = sql_queries.get_label_tasks(engine, user_id)

    if df_label_tasks is not None:
        resp = make_response(df_label_tasks.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No users found'), 404)
        resp.mimetype = "application/javascript"
        return resp


# ---------------  POST requests ---------------


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@ebp.route('/image_labeler/api/v1.0/login', methods=['POST'])
def login():
    engine = current_app.config['engine']

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    user_email = request.json.get('email', None)
    user_password = request.json.get('password', None)

    if not user_email:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not user_password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user_id = sql_queries.get_user_id(engine, user_email, user_password)

    if user_id is None:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = fje.create_access_token(identity='user_id={}'.format(user_id), expires_delta=False)

    return jsonify(access_token=access_token), 200


@ebp.route('/image_labeler/api/v1.0/user_id', methods=['GET'])
@fje.jwt_required
def get_user_id_from_access_token():
    """
    Get user's ID from their access token

    :return: user ID
    """

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id = ua.get_user_id_from_token(user_identity)

    resp = make_response(jsonify(user_id=user_id), 200)
    resp.mimetype = "application/javascript"
    return resp


@ebp.route('/image_labeler/api/v1.0/unlabeled_images/label_tasks/<int:label_task_id>', methods=['GET'])     # TODO: should be PUT request?
@fje.jwt_required
def get_unlabeled_image_id(label_task_id):
    """
    Get ID of a new image for the given label task, that has not yet been labeled or being labeled by another user

    Creates a label record to keep track of label history for this combination of user, input data item and label task.
    Can optionally give shuffle=true to shuffle data before sorting by priority

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :return:
    """

    engine = current_app.config['engine']

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id = ua.get_user_id_from_token(user_identity)

    # check if data must be shuffled before sorting by priority

    if request.is_json:
        shuffle = request.json.get('shuffle', False)
    else:
        shuffle = False

    try:
        df_unlabeled = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id, user_id, shuffle=shuffle,
                                                                      n=1)

        if df_unlabeled is None:
            resp = make_response(jsonify(error='No unlabeled input data found for this label task'), 404)
            resp.mimetype = "application/javascript"
            return resp
        else:
            try:
                input_data_id = int(df_unlabeled['input_data_id'][0])
            except:
                resp = make_response(jsonify(error='Error retrieving unlabeled input_data_id'), 500)
                resp.mimetype = "application/javascript"
                return resp
            else:
                label_id = sql_queries.create_new_label(engine,
                                                        input_data_id=input_data_id,
                                                        label_task_id=label_task_id,
                                                        user_id=user_id)

                if label_id is None:
                    resp = make_response(jsonify(error='Could not create label. Possibly due to a clash with existing '
                                                       'label ID'), 500)
                    resp.mimetype = "application/javascript"
                    return resp
                else:
                    resp = make_response(jsonify(input_data_id=input_data_id, label_id=label_id), 200)
                    resp.mimetype = "application/javascript"
                    return resp

    except Exception:
        resp = make_response(jsonify(error='Bad request'), 400)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/label_history/label_tasks/<int:label_task_id>/input_data/<int:input_data_id>',
           methods=['POST'])
@fje.jwt_required
def store_label(label_task_id, input_data_id):
    """
    Store the label for a particular label task, user and input data item

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :param input_data_id: ID of the input data item that has been labeled
    :return:
    """

    engine = current_app.config['engine']

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id = ua.get_user_id_from_token(user_identity)

    if not request.json:
        resp = make_response(jsonify(error='Must use JSON format'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if 'label_serialised' not in request.json:
        resp = make_response(jsonify(error='Requires serialised ground truth label to perform request'), 400)
        resp.mimetype = "application/javascript"
        return resp

    label_json = request.json.get('label_serialised', None)

    # convert the label from JSON format to a string, which can be stored in the database

    label_json_serialised = json.dumps(label_json)

    try:
        # find the label that the serialised label corresponds to

        label_id = sql_queries.get_label_id(engine,
                                            user_id=user_id,
                                            label_task_id=label_task_id,
                                            input_data_id=input_data_id)

        if label_id is None:
            resp = make_response(jsonify(error='Could not find label ID'), 404)
            resp.mimetype = "application/javascript"
            return resp
        else:
            # store a new label history record containing this serialised label

            label_hist_id = sql_queries.create_new_label_history(engine,
                                                                 label_id=label_id,
                                                                 serialised_label=label_json_serialised)

            if label_hist_id is None:
                resp = make_response(jsonify(error='Could not create label history record'), 500)
                resp.mimetype = "application/javascript"
                return resp
            else:
                resp = make_response(jsonify(label_id=label_id, label_hist_pks=label_hist_id), 200)
                resp.mimetype = "application/javascript"
                return resp
    except Exception:
        resp = make_response(jsonify(error='Bad request'), 400)
        resp.mimetype = "application/javascript"
        return resp


@ebp.route('/image_labeler/api/v1.0/input_data', methods=['POST'])
@fje.jwt_required
def upload_input_data_item():
    """
    Store the input data item's path
    :return:
    """

    engine = current_app.config['engine']

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

    if is_admin is None or not is_admin:
        resp = make_response(jsonify(error='Not permitted to add input data items. Must be an admin user.'), 403)
        resp.mimetype = "application/javascript"
        return resp

    if not request.json:
        resp = make_response(jsonify(error='Must use JSON format'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if 'input_data_path' not in request.json:
        resp = make_response(jsonify(error='Requires input_data_path to be specified'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if 'dataset_id' not in request.json:
        resp = make_response(jsonify(error='Requires dataset_id to be specified'), 400)
        resp.mimetype = "application/javascript"
        return resp

    input_data_path = request.json.get('input_data_path', None)
    dataset_id = request.json.get('dataset_id', None)

    try:
        dataset_id = int(dataset_id)
    except:
        resp = make_response(jsonify(error='dataset_id must be an integer'), 400)
        resp.mimetype = "application/javascript"
        return resp

    # calculate the hash of the file, which can be used to identify the file contents uniquely

    hash = du.calculate_file_hash(input_data_path)

    if hash is None:
        resp = make_response(jsonify(error='File does not exist at input_data_path: {}'.format(input_data_path)), 404)
        resp.mimetype = "application/javascript"
        return resp

    try:
        # insert new input_data item into database

        input_data_id = sql_queries_admin.create_new_input_data_item(engine,
                                                                     input_data_path=input_data_path,
                                                                     dataset_id=dataset_id,
                                                                     sha1_hash=hash)

        if input_data_id is None:
            resp = make_response(jsonify(error='Could not find label ID'), 404)
            resp.mimetype = "application/javascript"
            return resp
        else:
            resp = make_response(jsonify(input_data_id=input_data_id), 200)
            resp.mimetype = "application/javascript"
            return resp
    except Exception:
        resp = make_response(jsonify(error='Bad request'), 400)
        resp.mimetype = "application/javascript"
        return resp


# ---------------  PATCH requests ---------------


@ebp.route('/image_labeler/api/v1.0/labels/<int:label_id>', methods=['PATCH'])
@fje.jwt_required
def update_label_fields(label_id):
    """
    Update status fields of a specific label

    :param label_id:
    :return:
    """

    engine = current_app.config['engine']

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    is_admin = sql_queries_admin.is_user_an_admin(engine, user_id_from_auth)

    # only the user who created the label or an admin user may update the label fields

    df_label = sql_queries.get_label_by_id(engine, label_id)

    if df_label is None:
        resp = make_response(jsonify(error='Label does not exist'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if df_label['user_id'][0] != user_id_from_auth:
        if is_admin is None or not is_admin:
            resp = make_response(jsonify(error='Not permitted to perform this update. Must be an admin user or the '
                                               'owner of the label.'), 403)
            resp.mimetype = "application/javascript"
            return resp

    if not request.json:
        resp = make_response(jsonify(error='Must use JSON format'), 400)
        resp.mimetype = "application/javascript"
        return resp

    fields = {'user_complete': {'value': None, 'type': bool, 'admin_only': False},
              'needs_improvement': {'value': None, 'type': bool, 'admin_only': True},
              'admin_complete': {'value': None, 'type': bool, 'admin_only': True},
              'paid': {'value': None, 'type': bool, 'admin_only': True},
              'user_comment': {'value': None, 'type': str, 'admin_only': False},
              'admin_comment': {'value': None, 'type': str, 'admin_only': True}}

    for field, params in fields.items():
        val = request.json.get(field, None)
        if field in request.json:
            # check that user has correct privileges to update the given field
            if params['admin_only'] and not is_admin:
                resp = make_response(jsonify(error='Not permitted to perform this update. Must be an admin user to'
                                                   'modify field "{}".'.format(field)), 403)
                resp.mimetype = "application/javascript"
                return resp

            if isinstance(val, params['type']):
                fields[field]['value'] = request.json.get(field, None)
            else:
                if not request.json:
                    resp = make_response(jsonify(error='Parameter {} is of the wrong format'.format(field)), 400)
                    resp.mimetype = "application/javascript"
                    return resp

    fields_to_update = {field: v['value'] for field, v in fields.items() if v['value'] is not None}

    if len(fields_to_update) > 0:
        label_id_returned = sql_queries.update_label_status(engine, label_id=label_id, **fields_to_update)

        if label_id_returned is None:
            return jsonify({"msg": "Could not update label field(s)"}), 400
        else:
            return jsonify({"msg": "Updated label fields(s) successfully"}), 200
    else:
        return jsonify({"msg": "No field(s) to update. Check that you have specified valid field names and value "
                               "types"}), 400
