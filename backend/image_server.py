from flask import Flask, jsonify, request, abort, send_file, make_response
from flask_cors import CORS, cross_origin
import flask_jwt_extended as fje
import json
from sqlalchemy import create_engine

from backend.lib import sql_queries, user_authentication as ua

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

# https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
# pip install -U flask-cors
CORS(app, resources={r"/*": {"origins": "*"}})

config = {'username': 'postgres',
          'password': 'postgres',
          'ip': 'localhost',
          'database_name': 's3_label'}

engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(config['username'],
                                                              config['password'],
                                                              config['ip'],
                                                              config['database_name']))


# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 's3label-completely-secret'  # this should be kept secret!
jwt = fje.JWTManager(app)


# ---------------  GET requests ---------------


@app.route('/')
def homepage():
    return json.dumps({'message': 'You have found the S3 Label image server!'}), 200


@app.route('/image_labeler/api/v1.0/label_tasks', methods=['GET'])
@fje.jwt_required
def get_label_tasks():
    df_label_tasks = sql_queries.get_label_tasks(engine)

    if df_label_tasks is not None:
        resp = make_response(df_label_tasks.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    else:
        resp = make_response(jsonify(error='No label tasks found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@app.route('/image_labeler/api/v1.0/input_images/<int:input_image_id>', methods=['GET'])
@fje.jwt_required
def get_image(input_image_id):
    im_path = sql_queries.get_input_data_path(engine, input_image_id)

    if im_path is not None:
        return send_file(im_path)
    else:
        resp = make_response(jsonify(error='Input data item not found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@app.route('/image_labeler/api/v1.0/labeled_data/label_tasks/<int:label_task_id>/users/<int:user_id>', methods=['GET'])
@fje.jwt_required
def get_labeled_data(label_task_id, user_id):
    # check that the user has permission to get the requested data: admin users can get any user's data, but an
    # ordinary user can only get their own data

    user_identity = fje.get_jwt_identity()
    user_id_from_auth = ua.get_user_id_from_token(user_identity)

    # TODO: need to check if user is an admin user or not
    if not ua.check_user_permitted(user_id_from_auth, user_id, admin_ids=[]):
        resp = make_response(jsonify(error='Not permitted to view this content'), 403)
        resp.mimetype = "application/javascript"
        return resp

    # get the ID of the input data item to end the selection at

    input_data_id = request.args.get('input_image_id', None)
    num_labeled_images = request.args.get('num_labeled_images', None)

    if input_data_id is None:
        resp = make_response(jsonify(error='Need to specify input data ID'), 400)
        resp.mimetype = "application/javascript"
        return resp

    print('input_image_id:', input_data_id, 'num_labeled_images:', num_labeled_images)

    try:
        df_input_data = sql_queries.get_recent_labeled_input_data(engine,
                                                                  user_id=user_id,
                                                                  label_task_id=label_task_id,
                                                                  input_data_id=int(input_data_id),
                                                                  n=num_labeled_images,
                                                                  include_current_input_data=False)

        resp = make_response(df_input_data.to_json(orient='records'), 200)
        resp.mimetype = "application/javascript"
        return resp
    except Exception:
        resp = make_response(jsonify(error='No labeled data found for this user and/or label task'), 404)
        resp.mimetype = "application/javascript"
        return resp


# ---------------  POST requests ---------------


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/image_labeler/api/v1.0/login', methods=['POST'])
def login():
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


@app.route('/image_labeler/api/v1.0/unlabeled_images/label_tasks/<int:label_task_id>', methods=['PUT'])
@fje.jwt_required
def get_unlabeled_image_id(label_task_id):
    """
    Get ID of a new image for the given label task, that has not yet been labeled or being labeled by another user

    Creates a label record to keep track of label history for this combination of user, input data item and label task.

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :return:
    """

    if not request.json:
        resp = make_response(jsonify(error='Must use JSON format'), 400)
        resp.mimetype = "application/javascript"
        return resp

    if 'user_id' not in request.json or 'password' not in request.json:
        resp = make_response(jsonify(error='Requires user ID and password to perform request'), 401)
        resp.mimetype = "application/javascript"
        return resp

    # get ID of user

    user_identity = fje.get_jwt_identity()
    user_id = ua.get_user_id_from_token(user_identity)

    try:
        input_data_id = sql_queries.get_next_unlabeled_input_data_item(engine, label_task_id)

        if input_data_id is None:
            resp = make_response(jsonify(error='No input data found for this label task'), 404)
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


@app.route('/image_labeler/api/v1.0/label_history/label_tasks/<int:label_task_id>/input_data/<int:input_data_id>',
           methods=['POST'])
@fje.jwt_required
def store_label(label_task_id, input_data_id):
    """
    Store the label for a particular label task, user and input data item

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :param input_data_id: ID of the input data item that has been labeled
    :return:
    """

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

    label_serialised = request.json.get('label_serialised', None)

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
                                                                 serialised_label=label_serialised)

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


if __name__ == '__main__':
    app.run(debug=True)
