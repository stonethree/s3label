export function isBoundingBoxLargeEnough(startCoord, endCoord) {
    // check if path has non-negligible area
    var x_min = Math.min(startCoord[0], endCoord[0]);
    var x_max = Math.max(startCoord[0], endCoord[0]);
    var y_min = Math.min(startCoord[1], endCoord[1]);
    var y_max = Math.max(startCoord[1], endCoord[1]);

    if (Math.abs(x_min - x_max) < 5 || Math.abs(y_min - y_max) < 5) {
        return false;
    }
    else {
        return true;
    }
}

export function isPointInBoundingBox(selX, selY, box) {
    var x = [(box.bounding_box.x), (box.bounding_box.x + box.bounding_box.boxWidth)];
    var y = [(box.bounding_box.y), (box.bounding_box.y + box.bounding_box.boxHeight)];

    var x_min = Math.min(...x);
    var x_max = Math.max(...x);
    var y_min = Math.min(...y);
    var y_max = Math.max(...y);

    if ((x_min <= selX) && (selX <= x_max) && (y_min <= selY) && (selY <= y_max)) {
        return true;
    } else {
        return false;
    }
}

export function addPaddingOffset(bounding_boxes, padX, padY) {
    // add the padding from the left and top borders of the canvas, so that we include padding in the displayed coordinates

    for (let i = 0; i < bounding_boxes.length; i++) {
        bounding_boxes[i].bounding_box.x += padX;
        bounding_boxes[i].bounding_box.y += padY;
    }

    return bounding_boxes;
}


export function removePaddingOffset(bounding_boxes, padX, padY) {
    // subtract the padding from the left and top borders of the canvas, so that we don't include padding in the saved coordinates

    for (let i = 0; i < bounding_boxes.length; i++) {
        bounding_boxes[i].bounding_box.x -= padX;
        bounding_boxes[i].bounding_box.y -= padY;
    }

    return bounding_boxes;
}