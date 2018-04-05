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
        abort(404)


@app.route('/image_labeler/api/v1.0/unlabeled_images/label_task/<int:label_task_id>', methods=['GET'])
def get_unlabeled_image_id(label_task_id):
    """
    Get ID of a new image for the given label task, that has not yet been labeled or being labeled by another user

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :return:
    """

    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', None)
    print('offset:', offset, 'limit:', limit)

    try:
        if limit is not None:
            limit = int(limit)

        df_unlabeled_images = sql_queries.get_unlabeled_images(label_task_id, engine, num_images=limit)

        if df_unlabeled_images is None:
            abort(404)
        else:
            df_input_data_ids = df_unlabeled_images[['input_data_id']]

            resp = make_response(df_input_data_ids.to_json(orient='records'), 200)
            resp.mimetype = "application/javascript"
            return resp
    except Exception:
        abort(400)


@app.route('/image_labeler/api/v1.0/input_images/<int:input_image_id>', methods=['GET'])
def get_image(input_image_id):
    im_path = sql_queries.get_input_data_path(input_image_id, engine)

    if im_path is not None:
        return send_file(im_path)
    else:
        abort(404)


# @app.route('/image_labeler/api/v1.0/tasks', methods=['POST'])
# def create_task():
#     if not request.json or not 'title' in request.json:
#         abort(400)
#     task = {
#         'id': tasks[-1]['id'] + 1,
#         'title': request.json['title'],
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task)
#     return jsonify({'task': task}), 201


if __name__ == '__main__':
    app.run(debug=True)
