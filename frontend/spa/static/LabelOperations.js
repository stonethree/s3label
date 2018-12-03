export function getLabel(active_tool, coordPath, coords) {
    switch (active_tool) {
        case 'freehand':
        case 'polygon':
            return {regions: [coordPath],
                    inverted: false}
        case 'rectangle':
            return {x: coordPath[0][0],
                    y: coordPath[0][1],
                    boxWidth: coords.x - coordPath[0][0],
                    boxHeight: coords.y - coordPath[0][1]}
        default:
    }
}

export function isLabelLargeEnough(coordPath) {
    // check if path has non-negligible area
    //console.log('coordPath:');
    //console.log(coordPath);

    var x_min = Math.min(...coordPath.map(p => p[0]));
    var x_max = Math.max(...coordPath.map(p => p[0]));
    var y_min = Math.min(...coordPath.map(p => p[1]));
    var y_max = Math.max(...coordPath.map(p => p[1]));

    //console.log('x length: ' + Math.abs(x_min - x_max));
    //console.log('y length: ' + Math.abs(y_min - y_max));

    if (Math.abs(x_min - x_max) < 5 || Math.abs(y_min - y_max) < 5) {
        return false;
    }
    else {
        return true;
    }
}

export function isPointInLabel(selX, selY, labels) {
    switch (labels.type) {
        case 'freehand':
        case 'polygon':
            console.log('determining if point is in label type polygon...')
            for (var count = 0; count < labels.label.regions.length; j++) {
                var cornersX = labels.label.regions[count].map(p => p[0]);
                var cornersY = labels.label.regions[count].map(p => p[1]);

                var i, j = cornersX.length - 1;
                var oddNodes = false;

                var polyX = cornersX;
                var polyY = cornersY;

                for (i = 0; i < cornersX.length; i++) {
                    if ((polyY[i] < selY && polyY[j] >= selY || polyY[j] < selY && polyY[i] >= selY) && (polyX[i] <= selX || polyX[j] <= selX)) {
                        oddNodes ^= (polyX[i] + (selY - polyY[i]) / (polyY[j] - polyY[i]) * (polyX[j] - polyX[i]) < selX);
                    }
                    j = i;
                }

                if (oddNodes == 1) {
                    return true;
                } else {
                    return false;
                }
            }            
        case 'rectangle':
            var x = [(labels.label.x), (labels.label.x + labels.label.boxWidth)];
            var y = [(labels.label.y), (labels.label.y + labels.label.boxHeight)];

            var x_min = Math.min(...x);
            var x_max = Math.max(...x);
            var y_min = Math.min(...y);
            var y_max = Math.max(...y);

            if ((x_min <= selX) && (selX <= x_max) && (y_min <= selY) && (selY <= y_max)) {
                return true;
            } else {
                return false;
            }
        default:
    }
    
}

export function addPaddingOffset(labels, padX, padY) {
    // add the padding from the left and top borders of the canvas, so that we include padding in the displayed coordinates

    for (let i = 0; i < labels.length; i++) {
        switch (labels[i].type) {
            case 'freehand':
            case 'polygon':
                for (let j = 0; j < labels[i].label.regions.length; j++) {
                    labels[i].label.regions[j] = labels[i].label.regions[j].map(coords => [coords[0] + padX, coords[1] + padY]);
                }
                break;
            case 'rectangle':
                labels[i].label.x += padX;
                labels[i].label.y += padY;
                break;
            default:
        }
    }

    return labels;
}

export function removePaddingOffset(labels, padX, padY) {
    // subtract the padding from the left and top borders of the canvas, so that we don't include padding in the saved coordinates

    for (let i = 0; i < labels.length; i++) {
        switch (labels[i].type) {
            case 'freehand':
            case 'polygon':
                for (let j = 0; j < labels[i].label.regions.length; j++) {
                    labels[i].label.regions[j] = labels[i].label.regions[j].map(coords => [coords[0] - padX, coords[1] - padY]);
                }
                break;
            case 'rectangle':
                labels[i].label.x -= padX;
                labels[i].label.y -= padY;
                break;
            default:
        }
    }

    return labels;
}