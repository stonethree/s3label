import { extractColor, formatColor } from './color_utilities'
import { addPaddingOffset,
        removePaddingOffset,
        setLabelCoords } from './LabelOperations'

//sets the fill color of the label
export function setColor (vm, rgb, alpha) {
    vm.ctx.fillStyle = formatColor(rgb, alpha);
    return vm;
}

export function drawAllLabels(vm, labels_list, mult) {
    vm.ctx.lineWidth = vm.stroke_thickness;
    vm.ctx.clearRect(0, 0, vm.ctx.canvas.width, vm.ctx.canvas.height);

    let shown_labels = JSON.parse(JSON.stringify(labels_list));
    shown_labels = removePaddingOffset(shown_labels, vm.padX, vm.padY);
    shown_labels = setLabelCoords(shown_labels, mult);
    shown_labels = addPaddingOffset(shown_labels, vm.padX, vm.padY);

    if (!vm.hide_labels) {
        for (let i = 0; i < shown_labels.length; i++) {
            switch (shown_labels[i].type) {
                case 'freehand':
                case 'polygon':
                    drawPolygon(vm, shown_labels[i]);
                    break;
                case 'rectangle':
                    drawBoundingBox(vm, shown_labels[i]);
                    break;
                case 'point':
                    drawPoint(vm, shown_labels[i]);
                    break;
                case 'circle':
                    drawPoint(vm, labels_list[i]);
                    break;
                default:
            }
            
        }
    }
}

export function drawPoint(vm, point) {
    // console.log("Drawing point");
    vm = setColor(vm, vm.label_colors[point.label_class], vm.opacity);

    vm.ctx.beginPath();
    let fstyle = vm.ctx.fillStyle;
    vm.ctx.fillStyle = fstyle;
    if (point.selected) {
        var currentStrokeStyle = vm.ctx.strokeStyle;
        vm.ctx.strokeStyle = "#FF0000";
        vm.ctx.setLineDash([4, 4]);
    }
    // console.log(point);
    vm.ctx.arc(point.label.x, point.label.y, point.label.radius, 0, Math.PI*2);
    vm.ctx.closePath();
    
    vm.ctx.stroke();
    vm.ctx.fill();
    // vm.ctx.closePath();
    // vm.ctx.strokeStyle = currentStrokeStyle;
    vm.ctx.beginPath();
    vm.ctx.setLineDash([]);

    var currentColour = vm.ctx.currentColour

    if (point.selected) {
        vm.ctx.fillStyle = "#FF0000"
    } else {
        vm.ctx.fillStyle = "#000000"
    }
    

    if(point.type == "circle") {


        // just a comment
        // this.setColor([0, 0, 0], 1);
        vm.ctx.moveTo(point.label.x, point.label.y);
        vm.ctx.arc(point.label.x, point.label.y, 2 , 0, Math.PI*2);

    }    

    vm.ctx.stroke();
    vm.ctx.fill();

    vm.ctx.strokeStyle = currentStrokeStyle;
    vm.ctx.fillStyle = fstyle;
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

export function drawLiveCircle(vm) {
    if(vm.active_tool != 'circle') {
        return;
    }
    let x = vm.last_mouse_pos[0];
    let y = vm.last_mouse_pos[1];
    vm.ctx_live.fillStyle = formatColor(vm.label_colors[vm.active_label], vm.opacity);
    //vm.ctx.fillStyle = formatColor([0, 255, 0], 0.5);
    vm.ctx_live.beginPath();
    vm.ctx_live.moveTo(x + vm.circle_radius, y);
    vm.ctx_live.arc(x, y, vm.circle_radius , 0, Math.PI*2);

    vm.ctx_live.fill();
    vm.ctx_live.fillStyle = formatColor([0, 0, 0], 1);
    vm.ctx_live.moveTo(x, y);
    vm.ctx_live.arc(x, y, 2 , 0, Math.PI*2);
    
    vm.ctx_live.stroke();
}