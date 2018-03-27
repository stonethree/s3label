function convertPolygonToPath(polygon) {
    return polygon.regions[0];
}

function convertPathToPolygon(path) {
    return {
        regions: [path],
        inverted: false
    };
}