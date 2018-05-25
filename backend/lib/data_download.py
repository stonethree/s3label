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


def binary_im_from_polygon_label(polygons, w, h):
    """
    Create a binary image from a list of polygons, each of which can have one or more path regions.

    Fill all the polygon regions.

    :param polygons:
    :param w:
    :param h:
    :return:
    """

    mask = np.zeros((h, w), dtype=np.float32)

    logger.debug('')

    for poly in polygons:
        for region in poly['polygon']['regions']:
            # TODO: apply padding offset here (temporary solution: must fix properly)

            coords = [np.array(region, dtype=np.int32)]

            offset = 2 * np.array([80, 80])
            coords = np.subtract(coords, offset)

            cv2.fillPoly(mask, coords, (255.0,), 16, 0)

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
