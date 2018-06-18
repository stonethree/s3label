import numpy as np
import cv2
import json
import os
from PIL import Image
import logging


logger = logging.getLogger(__name__)


def get_polygon_regions_from_serialised_label(label_string):
    """
    Extract polygon paths from a serialised label

    :param label_string: serialised JSON object representing a list of polygons
    :return:
    """

    return json.loads(label_string)


def binary_im_from_polygon_label(polygons, w, h, mode='filled_polygon'):
    """
    Create a binary image from a list of polygons, each of which can have one or more path regions.

    Fill all the polygon regions.

    :param polygons:
    :param w:
    :param h:
    :param mode: what type of binary image to generate (filled_polygon, polygon_edge, center_dot,
        unit_vectors_from_edges)
    :return:
    """

    mask = np.zeros((h, w), dtype=np.float32)

    logger.debug('')

    for i, poly in enumerate(polygons):
        for region in poly['polygon']['regions']:
            # TODO: apply padding offset here (temporary solution: must fix properly)

            coords = [np.array(region, dtype=np.int32)]

            offset = 2 * np.array([80, 80])
            coords = np.subtract(coords, offset)

            if mode == 'filled_polygon':
                cv2.fillPoly(mask, coords, (255.0,), 16, 0)
            elif mode == 'polygon_edge':
                cv2.polylines(mask, coords, True, (255.,))
            elif mode == 'center_dot':
                center = np.mean(coords[0], axis=0)
                mask[int(center[1]), int(center[0])] = 255.
            elif mode == 'filled_polygon_instances':
                cv2.fillPoly(mask, coords, ((i + 1)*1.,), 16, 0)
            else:
                raise NotImplementedError('Mode is not defined')

    return mask


def get_image_dims(image_path):
    """
    Get width and height of an image file on disk

    :param image_path:
    :return:
    """

    if os.path.exists(image_path):
        im = Image.open(image_path)
        return im.size
    else:
        return None
