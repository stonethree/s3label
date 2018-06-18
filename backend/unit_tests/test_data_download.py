from backend.lib import data_download as dd


def test_get_polygon_regions_from_serialised_label():
    json_string = '[{"type": "freehand", "label": "foreground_object", "polygon": {"regions": [[[100.2, 200.1], ' \
                  '[130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]], "inverted": false}, "selected": true}]'

    label = dd.get_polygon_regions_from_serialised_label(json_string)

    assert len(label) == 1
    assert label[0]['type'] == 'freehand'
    assert label[0]['label'] == 'foreground_object'
    assert len(label[0]['polygon']['regions']) == 1
    assert label[0]['polygon']['regions'][0] == [[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]


def test_edge_im_from_polygon_label_when_two_polygons_have_same_label_classes():
    label = [{"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]],
                   "inverted": False}, "selected": True},
             {"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[200.2, 200.1], [230.4, 205.1], [232.2, 270.1], [202.1, 268.7]]],
                   "inverted": False}, "selected": False}
             ]
    im = dd.binary_im_from_polygon_label(label, 400, 350)

    assert im.shape == (350, 400)

    # TODO: to fix this test, we must fix the padding offset correction on the front-end

    assert im[236, 113] == 255
    assert im[10, 10] == 0
    assert im[236, 215] == 255


def test_edge_im_from_polygon_label():
        label = [{"type": "freehand",
                  "label": "foreground_object",
                  "polygon":
                      {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]],
                       "inverted": False}, "selected": True},
                 {"type": "freehand",
                  "label": "foreground_object",
                  "polygon":
                      {"regions": [[[200.2, 200.1], [230.4, 205.1], [232.2, 270.1], [202.1, 268.7]]],
                       "inverted": False}, "selected": False}
                 ]
        im = dd.binary_im_from_polygon_label(label, 400, 350, mode='polygon_edge')

        assert im.shape == (350, 400)

        # TODO: to fix this test, we must fix the padding offset correction on the front-end

        assert im[236, 113] == 255
        assert im[10, 10] == 0
        assert im[236, 215] == 255


def test_center_dot_from_polygon_label():
    label = [{"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]],
                   "inverted": False}, "selected": True},
             {"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[200.2, 200.1], [230.4, 205.1], [232.2, 270.1], [202.1, 268.7]]],
                   "inverted": False}, "selected": False}
             ]
    im = dd.binary_im_from_polygon_label(label, 400, 350, mode='center_dot')

    assert im.shape == (350, 400)

    # TODO: to fix this test, we must fix the padding offset correction on the front-end

    assert im[236, 113] == 255
    assert im[10, 10] == 0
    assert im[236, 215] == 255


def test_filled_polygon_instances_from_polygon_label():
    label = [{"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[100.2, 200.1], [130.4, 205.1], [132.2, 270.1], [102.1, 268.7]]],
                   "inverted": False}, "selected": True},
             {"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[200.2, 200.1], [230.4, 205.1], [232.2, 270.1], [202.1, 268.7]]],
                   "inverted": False}, "selected": False},
             {"type": "freehand",
              "label": "foreground_object",
              "polygon":
                  {"regions": [[[240.2, 240.1], [270.4, 245.1], [272.2, 310.1], [242.1, 308.7]]],
                   "inverted": False}, "selected": False}
             ]
    im = dd.binary_im_from_polygon_label(label, 400, 350, mode='filled_polygon_instances')

    assert im.shape == (350, 400)

    # TODO: to fix this test, we must fix the padding offset correction on the front-end

    assert im.max() == 3
    assert im.min() == 0


def test_get_image_dims():
    assert dd.get_image_dims('test_images/image.jpg') == (480, 300)
