import { extractColor, formatColor } from './color_utilities'

//sets the fill color of the label
export function setColor (vm, rgb, alpha) {
    vm.ctx.fillStyle = formatColor(rgb, alpha);
    return vm;
}

export function drawAllLabels(vm, labels_list) {
    vm.ctx.lineWidth = vm.stroke_thickness;
    vm.ctx.clearRect(0, 0, vm.ctx.canvas.width, vm.ctx.canvas.height);

    if (!vm.hide_labels) {
        for (let i = 0; i < labels_list.length; i++) {
            switch (labels_list[i].type) {
                case 'freehand':
                case 'polygon':
                    drawPolygon(vm, labels_list[i]);
                    break;
                case 'rectangle':
                    drawBoundingBox(vm, labels_list[i]);
                    break;
                default:
            }
            
        }
    }
}

//Polygon or Freehand drawing function
export function drawPolygon(vm, polygon) {
    vm = setColor(vm, vm.label_colors[polygon.label_class], vm.opacity);
    let paths_to_draw = polygon.label.regions;

    if (polygon.selected) {
        // draw selected polygon

        var currentStrokeStyle = vm.ctx.strokeStyle;
        vm.ctx.strokeStyle = "#FF0000";
        vm.ctx.setLineDash([4, 4]);

        for (let j = 0; j < paths_to_draw.length; j++) {
            drawPath(vm, paths_to_draw[j]);
            //console.log(paths_to_draw[j]);
        }

        vm.ctx.strokeStyle = currentStrokeStyle;
        vm.ctx.setLineDash([]);
    }
    else {
        // draw unselected polygon

        for (let j = 0; j < paths_to_draw.length; j++) {
            drawPath(vm, paths_to_draw[j]);
        }
    }
}

export function drawPath(vm, path) {
    let w = vm.ctx.canvas.width;
    let h = vm.ctx.canvas.height;

    vm.ctx.beginPath();
    //clamping points within the image borders
    vm.ctx.moveTo(Math.max(vm.padX, Math.min(path[0][0], w - vm.padX)),
        Math.max(vm.padY, Math.min(path[0][1], h - vm.padY)));

    for (let i = 1; i < path.length; i++) {
        vm.ctx.lineTo(Math.max(vm.padX, Math.min(path[i][0], w - vm.padX)),
            Math.max(vm.padY, Math.min(path[i][1], h - vm.padY)));
    }

    vm.ctx.closePath();
    if (vm.use_stroke) {
        vm.ctx.stroke();
    }
    vm.ctx.fill();
}

//Rectangle drawing function
export function drawBoundingBox (vm, box) {
    var vm_new = vm;
    vm_new = setColor(vm, vm.label_colors[box.label_class], vm.opacity);
    vm_new.ctx.beginPath();
    if (box.selected) {
        // draw selected box
        var currentStrokeStyle = vm_new.ctx.strokeStyle;
        vm_new.ctx.strokeStyle = "#FF0000";
        vm_new.ctx.setLineDash([4, 4]);

        vm_new.ctx.rect(box.label.x, box.label.y, box.label.boxWidth, box.label.boxHeight);
        vm_new.ctx.stroke();
        
        vm_new.ctx.strokeStyle = currentStrokeStyle;
        vm_new.ctx.setLineDash([]);

        vm_new.ctx.fill();
    }
    else {
        // draw unselected box
        vm_new.ctx.rect(box.label.x, box.label.y, box.label.boxWidth, box.label.boxHeight);
        vm_new.ctx.stroke();
        
        vm_new.ctx.fill();
    }
    
}