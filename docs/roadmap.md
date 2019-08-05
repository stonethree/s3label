# Roadmap

These are some of the main items that could provide useful improvements to S3Label.

## User interface

Currently, certain admin tasks need to be done via SQL commands. While directly using SQL is very powerful, it isn't as simple to use for all users. 
This currently includes creating and assigning label tasks, and payment tracking. 
We would like to allow all of this to be done via the user interface, while still permitting power users to use SQL commands where they wish.

## Label types

It would be good to add image classification labels as an additional label type.

## Algorithm-assisted labeling

It can be useful to have an algorithm (trained machine learning model or other) provide an initial labeling attempt, which the user can then correct if needed. In certain situations and if the algorithm is good enough, this can be quite helpful in speeding up the labeling process.

## Easier deployment of production S3Label instance.

It is currently (relatively) quick and easy to deploy a development instance of S3Label. 
However, a bit more work is required to deploy a production instance. 
It would be useful to Dockerise S3Label to make this nice and easy.  

PR's on any of these or other items in our [Github Issues](https://github.com/stonethree/s3label/issues) would be very welcome!
