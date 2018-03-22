from flask import Flask, jsonify, request, abort, send_file
from flask_cors import CORS, cross_origin
import json

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

# https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
# pip install -U flask-cors
CORS(app)

datasets = [
    {
        'id': 1,
        'site': 'MGN',
        'sensor': 'Lynxx001',
        'description': 'Lynxx belt images',
    },
    {
        'id': 2,
        'site': 'MGN',
        'sensor': 'Lynxx002',
        'description': 'Lynxx belt images',
    },
    {
        'id': 3,
        'site': 'MGN',
        'sensor': 'Froth001',
        'description': 'Froth sensor images with bad lighting',
    },
    {
        'id': 4,
        'site': 'FQM_Kansanshi',
        'sensor': 'KanTruck001',
        'description': 'Truck tip images at night with large rocks',
    }
]


merged_datasets = [
    {
        'id': 1,
        'label_task_id': 1,
        'dataset_id': 1
    },
    {
        'id': 2,
        'label_task_id': 1,
        'dataset_id': 2
    },
    {
        'id': 3,
        'label_task_id': 2,
        'dataset_id': 3
    },
    {
        'id': 4,
        'label_task_id': 3,
        'dataset_id': 4
    }
]


label_tasks = [
    {
        'id': 1,
        'merged_datasets_id': 1,
        'title': 'Rock segmentation',
        'description': 'Trace the outline of all reasonably-sized rocks in the image',
    },
    {
        'id': 2,
        'merged_datasets_id': 2,
        'title': 'Froth segmentation',
        'description': 'Trace the boundaries of all bubbles in the image',
    },
    {
        'id': 3,
        'merged_datasets_id': 3,
        'title': 'Ore detection',
        'description': 'Trace the boundary of the ore on the back of the truck',
    }
]


input_images = [
    {
        'id': 1,
        'dataset_id': 1,
        'image_path': 'test_images/image.jpg',
        'priority': 5,
    },
    {
        'id': 2,
        'dataset_id': 1,
        'image_path': 'test_images/image2.jpg',
        'priority': 5,
    },
    {
        'id': 3,
        'dataset_id': 1,
        'image_path': 'test_images/image3.jpg',
        'priority': 6,
    },
    {
        'id': 4,
        'dataset_id': 1,
        'image_path': 'test_images/image4.jpg',
        'priority': 6,
    },
    {
        'id': 5,
        'dataset_id': 3,
        'image_path': 'test_images/image_test.jpg',
        'priority': 5,
    }
]


labeled_images = [
    {'id': 1,
     'input_image_id': 1,
     'label_task_id': 1,
     'user_id': 1,
     'timestamp_first_edit': '2018-03-22 09:38:22 UTC',
     'timestamp_last_edit': '2018-03-22 09:45:25 UTC',
     'label_path': 'path/to/image_gt.jpg',
     'labeled': True,
     'in_progress': False,
     'verified_done': False,
     },
    {'id': 2,
     'input_image_id': 2,
     'label_task_id': 1,
     'user_id': 1,
     'timestamp_first_edit': None,
     'timestamp_last_edit': None,
     'label_path': None,
     'labeled': False,
     'in_progress': True,
     'verified_done': False,
     }
]


users = [
    {'user_id': 1,
     'user_code': '3Hx45',
     'first_name': 'Shaun',
     'last_name': 'Irwin',
     },
    {'user_id': 2,
     'user_code': 'mountain goat',
     'first_name': 'Kristo',
     'last_name': 'Botha',
     }
]


def get_images_for_label_task(label_task_id):
    """
    Get list of images for the current label task

    :param label_task_id:
    :return:
    """

    # get IDs of datasets corresponding to this label task

    dataset_ids = [md['dataset_id'] for md in merged_datasets if md['label_task_id'] == label_task_id]

    # get all images in these datasets

    return [im for im in input_images if im['dataset_id'] in dataset_ids]


def get_unlabeled_image(images):
    """
    Get an unlabeled image from the list of images

    :param images: list of images
    :return: an unlabeled image
    """

    # unlabeled_ims = [im for im in images if im['']]

    if len(images) > 0:
        return images[0]
    else:
        return None


@app.route('/')
def homepage():
    return json.dumps({'message': 'You have found the S3 Label image server!'}), 200


@app.route('/image_labeler/api/v1.0/label_tasks', methods=['GET'])
def get_label_tasks():
    return jsonify({'label_tasks': label_tasks})


@app.route('/image_labeler/api/v1.0/datasets', methods=['GET'])
def get_datasets():
    return jsonify({'datasets': datasets})


@app.route('/image_labeler/api/v1.0/unlabeled_images/<int:label_task_id>', methods=['GET'])
def get_unlabeled_image_id(label_task_id):
    """
    Get ID of a new image for the given label task, that has not yet been labeled or being labeled by another user

    :param label_task_id: ID of the label task that we want to retrieve an image for
    :return:
    """

    image_list = get_images_for_label_task(label_task_id)

    unlabeled_image = get_unlabeled_image(image_list)

    if unlabeled_image is None:
        abort(404)
    else:
        return jsonify({'input_image_id': unlabeled_image['id']})


@app.route('/image_labeler/api/v1.0/input_images/<int:input_image_id>', methods=['GET'])
def get_image(input_image_id):
    matching_images = [im for im in input_images if im['id'] == input_image_id]

    if len(matching_images) > 0:
        im_path = matching_images[0]['image_path']

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
