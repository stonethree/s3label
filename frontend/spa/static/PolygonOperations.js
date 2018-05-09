
export function convertPolygonToPaths(polygon) {
    return polygon.regions;
}

export function convertPathToPolygon(path) {
    return {
        regions: [path],
        inverted: false
    };
}

export function isPointInPolygon(x, y, cornersX, cornersY) {

    var i, j = cornersX.length - 1;
    var oddNodes = false;

    var polyX = cornersX;
    var polyY = cornersY;

    for (i = 0; i < cornersX.length; i++) {
        if ((polyY[i] < y && polyY[j] >= y || polyY[j] < y && polyY[i] >= y) && (polyX[i] <= x || polyX[j] <= x)) {
            oddNodes ^= (polyX[i] + (y - polyY[i]) / (polyY[j] - polyY[i]) * (polyX[j] - polyX[i]) < x);
        }
        j = i;
    }

    if (oddNodes == 1) {
        return true;
    }
    else {
        return false;
    }
}

export function getSelectedPolygonIndex(polygons) {
    // get the index of the last selected polygon in the list

    var index = -1;

    for (var i = 0; i < polygons.length; i++) {
        if (polygons[i].selected) {
            index = i;
        }
    }

    return index;
}

export function isPolygonLargeEnough(path) {
    // check if path has non-negligible area

    var x_min = Math.min(...path.map(p => p[0]));
    var x_max = Math.max(...path.map(p => p[0]));
    var y_min = Math.min(...path.map(p => p[1]));
    var y_max = Math.max(...path.map(p => p[1]));

    if (Math.abs(x_min - x_max) < 5 || Math.abs(y_min - y_max) < 5) {
        return false;
    }
    else {
        return true;
    }
}


export function addPaddingOffset(polygons, padX, padY) {
    // add the padding from the left and top borders of the canvas, so that we include padding in the displayed coordinates

    for (let i = 0; i < polygons.length; i++) {
        for (let j = 0; j < polygons[i].polygon.regions.length; j++) {
            polygons[i].polygon.regions[j] = polygons[i].polygon.regions[j].map(coords => [coords[0] - padX, coords[1] - padY]);
        }
    }

    return polygons;
}


export function removePaddingOffset(polygons, padX, padY) {
    // subtract the padding from the left and top borders of the canvas, so that we don't include padding in the saved coordinates

    for (let i = 0; i < polygons.length; i++) {
        for (let j = 0; j < polygons[i].polygon.regions.length; j++) {
            polygons[i].polygon.regions[j] = polygons[i].polygon.regions[j].map(coords => [coords[0] + padX, coords[1] + padY]);
        }
    }

    return polygons;
}
