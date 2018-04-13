from flask import Flask, jsonify, request, abort, send_file, make_response
from flask_cors import CORS, cross_origin
import json
from sqlalchemy import create_engine

from backend.lib import sql_queries

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


# TODO: use JSON web tokens to perform logging in


# ---------------  GET requests ---------------


@app.route('/')
def homepage():
    return json.dumps({'message': 'You have found the S3 Label image server!'}), 200


@app.route('/image_labeler/api/v1.0/label_tasks', methods=['GET'])
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
def get_image(input_image_id):
    im_path = sql_queries.get_input_data_path(engine, input_image_id)

    if im_path is not None:
        return send_file(im_path)
    else:
        resp = make_response(jsonify(error='Input data item not found'), 404)
        resp.mimetype = "application/javascript"
        return resp


@app.route('/image_labeler/api/v1.0/labeled_data/label_task/<int:label_task_id>/user/<int:user_id>', methods=['GET'])
def get_labeled_data(label_task_id, user_id):
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


@app.route('/image_labeler/api/v1.0/unlabeled_images/label_task/<int:label_task_id>', methods=['POST'])
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

    user_id = request.json.get('user_id', None)
    password = request.json.get('password', None)

    # TODO: verify that user ID and password are valid

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


@app.route('/image_labeler/api/v1.0/label_history/label_task/<int:label_task_id>/input_data/<int:input_data_id>',
           methods=['POST'])
def store_label(label_task_id, input_data_id):
    """
    Store the label for a particular label task, user and input data item

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :param input_data_id: ID of the input data item that has been labeled
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

    if 'label_serialised' not in request.json:
        resp = make_response(jsonify(error='Requires serialised ground truth label to perform request'), 400)
        resp.mimetype = "application/javascript"
        return resp

    user_id = request.json.get('user_id', None)
    password = request.json.get('password', None)
    label_serialised = request.json.get('label_serialised', None)

    # TODO: verify that user ID and password are valid

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
