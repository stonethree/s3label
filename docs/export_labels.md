# Exporting Labels

Once data has been labeled you will want to export this data in some way for training your machine learning models. 
There are several ways in which to do this:
* Directly query the database via a SQL select query
* Use the REST API to get the raw JSON labels
* Use the REST API to generate label images from the JSON data and dump these images to disk on the S3Label server 

Each of these options is explained in more detail below.

## SQL select

It is possible to use a *SQL select* to query the *latest_label_history* view directly. This is a Postgres view that 
contains the most recent label for each image.

~~~ SQL
SELECT * FROM latest_label_history_per_input_item;
~~~

If you are using Python a convenient way to use get this data is using Pandas:

~~~ PYTHON
import psycopg2 as pg
import pandas.io.sql as psql

# get connected to the database
connection = pg.connect("dbname=<database_name> user=<username> password='<password>' host='<ip_address>'")

# fetch image paths with input data ID's
df_input_data = psql.read_sql("SELECT * FROM input_data", connection)

# fetch labels with input data ID's
df_labels_full = psql.read_sql("SELECT * FROM latest_label_history_per_input_item", connection)

# select only the labels for the specified label task
df_label_task = df_labels[df_labels['label_task_id'] == args.label_task_id]

# remove rows where the label does not exist
df_label_task = df_label_task[df_label_task['label_id'].notnull()]
df_label_task = df_label_task[df_label_task['label_serialised'].notnull()]

...
~~~

## Use the REST API to get the raw JSON labels

It is also possible to use the REST API to get the most recent labels for each image and dump the input images and their 
JSON labels to disk on the S3Label server.

First you will need to get an access token (i.e. JSON web token) to gain access to most of the REST API calls. 
You can query the API for an access token as follows:

~~~ bash
curl -X POST \
  https://label.stonethree.com/image_labeler/api/v1.0/login \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "<email address>",
    "password": "<password>"
}'
~~~

You can also find the token in your browser's local storage. Use the value for the *S3_ACCESS_TOKEN* key.

The following HTTP request will get the subset of labels for Label Task 5 where the label status is marked as 
*user complete* (i.e. the users who labeled the images have marked the images as "labeled"):

~~~ bash
curl -X POST \
  https://label.stonethree.com/image_labeler/api/v1.0/latest_label_history/label_task_id/5 \
  -H 'Authorization: Bearer <token>' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
    "label_status": "user_complete"
}'
~~~

The following HTTP request will get the subset of labels for Label Task 5 where the label status is marked as 
*admin complete* (i.e. an admin user has approved the labeling) and the images have specifically been marked for use
as test data (i.e. for evaluation of the machine learning model), rather than for training the model:

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

## Use the REST API to generate label images from the label JSON data

Another option that can be useful when using the labels for semantic segmentation or instance segmentation with image 
data is to have the S3Label back-end server generate image masks from the JSON data. 

Whereas the previous methods of exporting labels require a lot of post-processing to be done to convert the raw 
co-ordinates of the labels into a manner useful for machine learning model training, we can also have the S3Label 
server do this and then dump the generated label masks along with the corresponding images to disk on the S3Label server.

The following REST API call will generate the label mask images and save them and the input images to disk in the 
specified folder:

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

The *test_data* and *label_status* fields are optional. Use these to further filter the labels returned.

*gt_mode* can be one of the following:

| gt_mode                   |                                                                                       |
| -------------             |:-------------                                                                         |
| filled_polygon            | Generate filled polygons, all having the same fill value                              |
| polygon_edge              | Draw the edges of all polygons                                                        |
| center_dot                | Not yet tested, but it should generate a single dot at the centroid of each instance  |
| filled_polygon_instances  | Generate filled polygons, where each instance has a different integer value           |

*test_data* can be set to "true", "false" or the field can be omitted (default):

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
