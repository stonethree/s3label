# README

Use the following API call to generate ground truth image data:

~~~
curl -X PUT \
  https://label.stonethree.com/image_labeler/api/v1.0/label_images/label_task_id/5 \
  -H 'Authorization: Bearer <token>' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
	"output_folder": "/tmp/ground_truth_images/label_task_5_test",
	"suffix": "_gt4",
	"gt_mode": "filled_polygon_instances",
	"test_images": "true"
}'
~~~

*gt_mode* can be one of the following:

| gt_mode                   |                                                                                       |
| -------------             |:-------------                                                                         |
| filled_polygon            | Generate filled polygons, all having the same fill value                              |
| polygon_edge              | Draw the edges of all polygons                                                        |
| center_dot                | Not yet tested, but it should generate a single dot at the centroid of each instance  |
| filled_polygon_instances  | Generate filled polygons, where each instance has a different integer value           |

*test_images* can be set to "true", "false" or the field can be omitted (default)

| test_images       |                                                                                       |
| -------------     |:-------------                                                                         |
| true              | Only generate ground truth images for data marked as "test data"                      |
| false             | Only generate ground truth images for data *not* marked as "test data"                |
| (omitted)         | Generate ground truth data for all matching data                                      |

## Useful SQL queries

Delete duplicate input_data items from a particular dataset that has just been uploaded:

~~~
BEGIN;

delete from input_data i using duplicate_input_data d where i.input_data_id = d.input_data_id and i.dataset_id = 17 and i.timestamp_upload is not null;

select * from input_data where dataset_id = 17;

--rollback, so that we can test the query before executing (i.e. perform a dry run)
ROLLBACK;
~~~