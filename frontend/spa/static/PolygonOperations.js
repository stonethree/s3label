module.exports = {
    convertPolygonToPaths: convertPolygonToPaths,
    convertPathToPolygon: convertPathToPolygon,
    isPointInPolygon: isPointInPolygon,
    getSelectedPolygonIndex: getSelectedPolygonIndex,
    isPolygonLargeEnough: isPolygonLargeEnough,
  }


function convertPolygonToPaths(polygon) {
    return polygon.regions;
}

function convertPathToPolygon(path) {
    return {
        regions: [path],
        inverted: false
    };
}

function isPointInPolygon(x, y, cornersX, cornersY) {

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

function getSelectedPolygonIndex(polygons) {
    // get the index of the last selected polygon in the list

    var index = -1;

    for (var i = 0; i < polygons.length; i++) {
        if (polygons[i].selected) {
            index = i;
        }
    }

    return index;
}

function isPolygonLargeEnough(path) {
    // check if path has non-negligible area

    var x_min = Math.min(...currentPath.map(p => p[0]));
    var x_max = Math.max(...currentPath.map(p => p[0]));
    var y_min = Math.min(...currentPath.map(p => p[1]));
    var y_max = Math.max(...currentPath.map(p => p[1]));

    if (Math.abs(x_min - x_max) < 5 || Math.abs(y_min - y_max) < 5) {
        return false;
    }
    else {
        return true;
    }
}