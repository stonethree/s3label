# Exporting Labels

## How to generate ground truth labels and dump them to disk

There are currently two options for exporting the labels from the database via REST queries: getting all the raw JSON data or generating images from the labels.

It is also possible to use a *SQL select* to query the *latest_label_history* table directly.
 
### Getting the raw JSON data

~~~ bash
curl -X POST \
  https://label.stonethree.com/image_labeler/api/v1.0/latest_label_history/label_task_id/5 \
  -H 'Authorization: Bearer <token>' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
	"test_images": "true",
    "label_status": "admin_complete"
}'
~~~

The *test_data* and *label_status* fields are optional. Use these to further filter the labels returned.

### Generate ground truth images from the labels

Use the following API call to generate ground truth image data and dump it to disk (on the same machine where the backend is hosted):

~~~ bash
curl -X PUT \
  https://label.stonethree.com/image_labeler/api/v1.0/label_images/label_task_id/5 \
  -H 'Authorization: Bearer <token>' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
	"output_folder": "/tmp/ground_truth_images/label_task_5_test",
	"suffix": "_gt4",
	"gt_mode": "filled_polygon_instances",
	"test_data": "true",
    "label_status": "admin_complete"
}'
~~~

*gt_mode* can be one of the following:

| gt_mode                   |                                                                                       |
| -------------             |:-------------                                                                         |
| filled_polygon            | Generate filled polygons, all having the same fill value                              |
| polygon_edge              | Draw the edges of all polygons                                                        |
| center_dot                | Not yet tested, but it should generate a single dot at the centroid of each instance  |
| filled_polygon_instances  | Generate filled polygons, where each instance has a different integer value           |

*test_images* can be set to "true", "false" or the field can be omitted (default):

| test_data         |                                                                                       |
| -------------     |:-------------                                                                         |
| true              | Only generate ground truth images for data marked as "test data"                      |
| false             | Only generate ground truth images for data *not* marked as "test data"                |
| (omitted)         | Generate ground truth data for all matching data                                      |

*label_status* can be set to "admin_complete" (default) or "user_complete":

| label_status    |                                                                                       |
| -------------   |:-------------                                                                         |
| admin_complete  | Only generate ground truth images for data marked as "admin_complete" (i.e. admin user has approved this image)   |
| user_complete   | Only generate ground truth images for data marked as "user_complete" (i.e. user has marked this image as complete, but admin user has not necessarily approved the labeling yet)                |
