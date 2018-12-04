# FEATURES

## Format
A general format of JSON is used which will allow this to work on any platform. 

## Class of Users
The users are split into two tiers: admin and 'labellers'. Segmentation of users allows differentiation between users (admin) that assigns tasks and users ('labellers') that receives tasks.

## Instance Segmentation
Instance segmentation allows the user to draw over existing selections.
Once the drawing is done the new selection will not overlap existing selections.
 
![Image Segmentation](./visuals/segmentation.gif)

Support for other labeling types (e.g. bounding boxes, key points and image classes) is currently being added.

The label storage format (i.e. JSON) is very flexible thus allowing for all kinds of data such as audio, videos etc. to be stored.

## Importing Labels
Images can easily be imported from the hard drive.

## Exporting Labels
Label data can be exported to images that will be used in training.