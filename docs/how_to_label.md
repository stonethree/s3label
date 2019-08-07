# How to label images

* S3Label supports multiple types of labeling, including freehand, polygon, rectangle and circle.
* You may mix and match any of these label types in the same label task and image.
* Each label is assigned to a *label class*. This allows the labeler to distinguish between different pre-assigned label classes that have created by whoever set up the label task.

## Freehand label type

### Draw

To make a freehand selection, use the mouse to choose a point on the picture to start and drag around the section you would like to select then release the mouse.

![Freehand](./visuals/freehand.gif)

### Append

Hold in the SHIFT key while drawing the area to be appended to the currently selected label.

![Append](./visuals/append.gif)

### Erase

Hold in the ALT key while drawing the area to be erased from the currently selected label.

![Erase](./visuals/erase.gif)

## Polygon label type

Draw a custom polygon by clicking each vertex of the desired shape. Double click to complete the label.

## Rectangle label type

Click-drag a rectangular bounding box.

## Circle label type

Click-drag from the center of the circle to draw the label. You may then reposition the circle after initially drawing it.