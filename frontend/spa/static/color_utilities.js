export function extractColor(rgb_string) {
    // takes a string of format
    var rgb = JSON.parse(rgb_string)

    if (rgb.length == 3) {
        return rgb;
    }
    else {
        throw TypeError('Color string must have 3 RGB elements specified');
    }
}

export function formatColor(rgb, alpha) {
    return 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',' + alpha + ')';
}