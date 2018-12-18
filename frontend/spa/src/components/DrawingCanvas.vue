<template>
    <div class="canvas-section" style="position:static; display: inline;">
        <div id="canvasesdiv" style="position:relative;" @mousedown.passive="mouseDownHandler" @mouseup.passive="mouseUpHandler" @mousemove.passive="mouseMoveHandler">
            <canvas id="canvas-live" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 4; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <canvas id="canvas-fg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 3; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <canvas id="canvas-bg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <canvas id="canvas-pattern" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <span v-if="input_data_id == undefined" class="image-not-found">No more unlabeled images available for this label task. Thanks for the effort! 
                <br>You may choose to label images from another <router-link v-bind:to="'/label_tasks'" >label task</router-link> if any are available.
            </span>
        </div>
    </div>
</template>

<script>

import { mapGetters } from 'vuex'

import axios from "axios";

var baseUrl = process.env.API_ADDR;
axios.defaults.baseURL = baseUrl;

// label operations

var PolyBool = require('polybooljs');
import { getLabel,
         isLabelLargeEnough,
         isPointInLabel,
         getSelectedLabelIndex,
         addPaddingOffset,
         removePaddingOffset,
         setLabelCoords } from '../../static/LabelOperations'

import { drawAllLabels, drawCircle } from '../../static/DrawingOperations'

import LabelStatus from './LabelStatus'
import { getLatestLabeledImage } from '../../static/label_loading';


export default {
    name: 'drawing_canvas',
    props: {
        active_tool: {
        }, 
        active_mode: {
        }, 
        active_overlap_mode: {
        }, 
        active_label: {
        }, 
        input_data_id: {
            required: true
        }, 
        label_task_id: {
            required: true
        },
        stroke_thickness: {
            required: true,
            type: Number
        },
        use_stroke: {
            required: true,
            type: Boolean
        },
        opacity: {
            required: true,
            type: Number
        },
        brightness: {
            required: true,
            type: Number
        },
        contrast: {
            required: true,
            type: Number
        },
        clear_canvas_event: {
            required: false,
            type: Boolean,
            default: false
        },
        delete_event: {
            required: false,
            type: Boolean,
            default: false
        },
        deselect_event: {
            required: false,
            type: Boolean,
            default: false
        },
        undo_event: {
            required: false,
            type: Boolean,
            default: false
        },
        redo_event: {
            required: false,
            type: Boolean,
            default: false
        },
        hide_labels: {
            required: false,
            type: Boolean,
            default: false
        },
        increase_circle_event: {
            required: false,
            type: Boolean,
            default: false
        },
        decrease_circle_event: {
            required: false,
            type: Boolean,
            default: false
        },
        change_radio_event: {
            required: false,
            type: Boolean,
            default: false
        },
        switch_label_event: {
            required: false,
            type: Boolean,
            default: false
        },
        zoom_level: {
            required: true,
            type: Number
        },
    },
    data: function() {
        return {
            isDrawing: false,
            edited: false,
            coordPath: [],
            padX: 80,
            padY: 80,
            responseAsBlob: undefined,
            ctx: undefined,
            ctx_bg: undefined,
            label_status_toggler: {user_complete: false},
            labels: [],
            labels_redo: [],
            labels_undo: [],
            circleFlag: false,
            circle_radius: 20,
            last_mouse_pos: [],
            multiplier: 1,
        };
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_colors'
        ]),
        ...mapGetters('user_login', [
            'user_id'
        ]),
        ...mapGetters('image_labeling', [
            // 'input_data_id',
            'label_id'
        ]),
        drawingPermitted: function() {
            return this.input_data_id != undefined;
        }
    },
    beforeMount() {
        var msScroll = this.onMouseScroll;
        window.addEventListener('wheel',function(event){
                msScroll(event);
                return false;
            }, false);
    },
    mounted() {
        var el = document.getElementById('canvas-fg');
        var el2 = document.getElementById('canvas-bg');
        var el3 = document.getElementById('canvas-live');
        this.ctx = el.getContext('2d');
        this.ctx_bg = el2.getContext('2d');
        this.ctx_live = el3.getContext('2d');

        console.log('------ mounted page')

        // if an image ID is specified, get its corresponding label ID and load that image

        if (this.input_data_id != undefined) {
            this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
        }
        else {
            this.draw_image_unavailable_placeholder();
        }
    },
    watch: {
        stroke_thickness: function () {
            drawAllLabels(this, this.labels, this.multiplier);
        },
        use_stroke: function () {
            drawAllLabels(this, this.labels, this.multiplier);
        },
        opacity: function () {
            drawAllLabels(this, this.labels, this.multiplier);
        },
        brightness: function () {
            if (this.responseAsBlob != undefined) {
                this.showImage(this.responseAsBlob);
            }
        },
        contrast: function () {
            if (this.responseAsBlob != undefined) {
                this.showImage(this.responseAsBlob);
            }
        },
        input_data_id: function (new_input_data_id, old_input_data_id) {
            console.log('switching image...');
            
            if (new_input_data_id != undefined) {
                this.fetchAndDisplayImage(baseUrl + '/input_images/' + new_input_data_id);
            }
            else {
                this.draw_image_unavailable_placeholder();
            }
        },

        labels: function() {
            drawAllLabels(this, this.labels, this.multiplier);
        },

        clear_canvas_event: function() {
            this.clearCanvas();
            this.clearLiveCanvas();
            console.log('clear canvas event occured')
        },

        delete_event: function() {
            this.delete();
            console.log('delete event occured')
        },

        deselect_event: function() {
            this.deselect();
            console.log('deselect event occured')
        },

        undo_event: function() {
            this.undo();
            console.log('undo event occured')
        },

        redo_event: function() {
            this.redo();
            console.log('redo event occured')
        },

        hide_labels: function() {
            drawAllLabels(this, this.labels, this.multiplier);
        },
        increase_circle_event: function() {
            this.inc_circle_size();
        },

        decrease_circle_event: function() {
            this.dec_circle_size();
        },

        switch_label_event: function() {
            this.rerenderLiveCanvas();
            this.isDrawing = false;
        },

        change_radio_event: function(){
            this.radioEvent();
        },

        zoom_level: function() {
            this.multiplier = this.zoom_level/100;
            this.resize_canvas(this.multiplier);
        },
    },
    methods: {
        inc_circle_size: function(fast_res=false) {
            if(fast_res) {
                this.circle_radius += 8;
            } else {
                this.circle_radius += 1;
            }
            this.clearLiveCanvas();
            drawCircle(this, this.ctx_live, this.last_mouse_pos, this.circle_radius*this.multiplier);
        },

        dec_circle_size: function(fast_res=false) {
            if(this.circle_radius != 1){
                if(fast_res && this.circle_radius > 5) {
                    this.circle_radius -= 8;
                } else {
                    this.circle_radius -= 1;
                }
                this.clearLiveCanvas();
                drawCircle(this, this.ctx_live, this.last_mouse_pos, this.circle_radius*this.multiplier);
            }
        },

        onMouseScroll: function(e) {
            var fast_res = false;
            if(e.shiftKey) {
                fast_res = true;
                if(e.deltaY > 0) {
                    // scrolled up
                    this.inc_circle_size(fast_res);
                } else if(e.deltaY < 0 ) {
                    // scrolled down
                    this.dec_circle_size(fast_res);
                }
                e.stopPropagation();
                e.preventDefault();
            }


        },

        rerenderLiveCanvas: function() {
            this.clearLiveCanvas();
            drawCircle(this, this.ctx_live, this.last_mouse_pos, this.circle_radius*this.multiplier);
        },

        radioEvent: function() {
            this.clearLiveCanvas();
        },

        set_labels: function(labels) {
            // the parent component can set the labels using this method in order to load the labels from the backend

            let labls = JSON.parse(JSON.stringify(labels));     // deep copy

            // add the padding from the left and top borders of the canvas, so that we include padding in the displayed coordinates

            this.labels = addPaddingOffset(labls, this.padX, this.padY);

            console.log('labels set to: ', this.labels);

            this.edited = false;
        },

        fetch_labels: function() {
            // the parent component can fetch the labels using this method in order to save the labels to the backend

            let labls = JSON.parse(JSON.stringify(this.labels));     // deep copy

            // subtract the padding from the left and top borders of the canvas, so that we don't include padding in the saved coordinates

            return { labels: removePaddingOffset(labls, this.padX, this.padY),
                     edited: this.edited
            };
        },

        draw_image_unavailable_placeholder: function() {
            // draw a placeholder image to the canvas and state to the user that no unlabeled images found

            let canvas_bg = document.getElementById("canvas-bg");
            let canvas_fg = document.getElementById("canvas-fg");
            let canvas_lv = document.getElementById("canvas-live");
            let canvas_pattern = document.getElementById("canvas-pattern");
            let ctx2 = canvas_bg.getContext("2d");  

            let w = 600;
            let h = 400;

            this.setCanvasSize(canvas_bg, w, h, this.padX, this.padY);
            this.setCanvasSize(canvas_fg, w, h, this.padX, this.padY);
            this.setCanvasSize(canvas_lv, w, h, this.padX, this.padY);
            ctx2.fillStyle = "hsl(25, 40%, 100%)";
            ctx2.fillRect(this.padX, this.padY, w, h);

            this.draw_pattern(w, h);
        },

        getMousePos: function (canvas, event) {
            // https://stackoverflow.com/questions/17130395/real-mouse-position-in-canvas
            var rect = canvas.getBoundingClientRect();
            return {
                x: event.clientX - rect.left,
                y: event.clientY - rect.top
            };
        },

        mouseDownHandler: function (e) {
            var coords = this.getMousePos(this.ctx.canvas, e);

            if (coords.x == undefined || coords.y == undefined) {
                console.log("coords undef:" + coords);
            }

            // getting coords at zoom level 100%
            let tmpX = ((coords.x-this.padX)/this.multiplier)+this.padX;
            let tmpY = ((coords.y-this.padY)/this.multiplier)+this.padY;

            switch (this.active_tool) {
                case 'freehand':
                    this.labels_redo = [];
                    this.isDrawing = true;
                    this.ctx.lineJoin = this.ctx.lineCap = 'round';
                    this.ctx.beginPath();
                    this.ctx.moveTo(coords.x, coords.y);
                    this.coordPath.push([tmpX, tmpY]);
                    break;
                case 'polygon':
                    if (!this.isDrawing) {
                        console.log('drawing first point')
                        this.labels_redo = [];
                        this.isDrawing = true;
                        this.ctx.lineJoin = this.ctx.lineCap = 'round';
                        this.ctx.beginPath();
                        this.ctx.arc(coords.x, coords.y, 4, 0, Math.PI*2);
                        this.ctx.stroke();
                        this.ctx.moveTo(coords.x, coords.y);
                        this.coordPath.push([tmpX, tmpY]);
                    } else {
                        var lastPoint = this.coordPath[this.coordPath.length - 1];
                        console.log('lastpoint: x - ' + lastPoint[0] + ' y - ' + lastPoint[1]);
                        if (Math.abs(coords.x - (((lastPoint[0]-this.padX)*this.multiplier)+this.padX)) < 2 && Math.abs(coords.y - (((lastPoint[1]-this.padY)*this.multiplier)+this.padY)) < 2) {
                            this.processLabel(e);
                        } else {
                            // add point to current path
                            this.ctx.arc(coords.x, coords.y, 4, 0, Math.PI*2);
                            this.ctx.stroke();
                            this.ctx.lineTo(coords.x, coords.y);
                            this.coordPath.push([tmpX, tmpY]);
                        }
                        console.log('coordPath: ' + this.coordPath);
                    }
                    break;
                case 'rectangle':
                    this.isDrawing = true;
                    this.ctx.lineJoin = this.ctx.lineCap = 'miter';
                    this.ctx.moveTo(coords.x, coords.y);
                    this.coordPath.push([tmpX, tmpY]);
                    break;
                case 'point':
                    // mark current point and process it
                    this.coordPath = [];
                    this.processLabel(e);
                    break;
                case 'circle':
                    this.labels_redo = [];
                    this.coordPath = [];
                    //this.coordPath.push([coords.x, coords.y]);
                    this.processLabel(e);
                    break;
                case 'select':
                    // check which labels the point lies within
                    for (var i = 0; i < this.labels.length; i++) {
                        var selected = false;
                        if (isPointInLabel(coords.x, coords.y, this.labels[i]))
                        {
                            this.labels[i].selected = true;
                        } else {
                            this.labels[i].selected = false;
                        }
                    }
                    drawAllLabels(this, this.labels, this.multiplier);
                    break;
                
                default:
            }
        },

        mouseMoveHandler: function (e) {
            var coords = this.getMousePos(this.ctx.canvas, e);
            if (this.isDrawing) {
                if (this.active_tool == 'freehand') {
                    if (coords.x == undefined || coords.y == undefined) {
                        console.log("coords undef:" + coords);
                    }
                    this.ctx.lineTo(coords.x, coords.y);
                    this.ctx.stroke();

                    // getting coords at zoom level 100%
                    let tmpX = ((coords.x-this.padX)/this.multiplier)+this.padX;
                    let tmpY = ((coords.y-this.padY)/this.multiplier)+this.padY;

                    this.coordPath.push([tmpX, tmpY]);
                } else if (this.active_tool == 'rectangle') {
                    this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
                    drawAllLabels(this, this.labels, this.multiplier);
                    this.ctx.beginPath();

                    if (coords.x == undefined || coords.y == undefined) {
                        console.log("coords undef:" + coords);
                    }

                    // getting coords at zoom level (depending on multiplier)
                    let tmpX = ((this.coordPath[0][0]-this.padX)*this.multiplier)+this.padX;
                    let tmpY = ((this.coordPath[0][1]-this.padY)*this.multiplier)+this.padY;

                    this.ctx.rect(tmpX, tmpY, coords.x - tmpX, coords.y - tmpY);
                    this.ctx.stroke();
                }
            } else if (this.active_tool == 'circle') {
                this.last_mouse_pos = [coords.x, coords.y];
                this.clearLiveCanvas(); // TODO
                this.ctx_live.moveTo(coords.x, coords.y);
                drawCircle(this, this.ctx_live, this.last_mouse_pos, this.circle_radius*this.multiplier); // TODO

                if (coords.x == undefined || coords.y == undefined) {
                    console.log("coords undef:" + coords);
                }
            }
        },

        mouseUpHandler: function (e) {
            //processes label if active tool is not selected as polygon
            if(this.active_tool == 'circle') {
                this.isDrawing = false;
            }
            if(this.active_tool == 'point') {
                return;
            }
            if (this.isDrawing && this.active_tool != 'polygon') {
                this.processLabel(e);
            }
        },

        processLabel: function (e) {
            this.isDrawing = false;
            this.edited = true;

            var coords = this.getMousePos(this.ctx.canvas, e);
            
            //getting coords at zoom level 100%
            let tmpX = ((coords.x-this.padX)/this.multiplier)+this.padX;
            let tmpY = ((coords.y-this.padY)/this.multiplier)+this.padY;

            this.coordPath.push([tmpX, tmpY]);

            this.ctx.closePath();
            if (this.use_stroke) {
                    this.ctx.stroke();
            }
            this.ctx.fill();
            
            console.log('coordPath: ' + this.coordPath);

            // do not add label if it has zero area
            if (!isLabelLargeEnough(this.active_tool, this.coordPath) && this.active_tool != 'point') {
                console.log('label too small! discarding it')

                this.coordPath = [];
                drawAllLabels(this, this.labels, this.multiplier);
                return;
            }

            if (this.active_mode == 'new') {
                // deselect all previous labels

                for (let i = 0; i < this.labels.length; i++) {
                    this.labels[i].selected = false;
                }
            }

            var infos = {};
            if(this.active_tool == 'circle') {
                infos['circle_radius'] = this.circle_radius;
            }
            
            let tmpCoords = [tmpX, tmpY];
            let currentLabel = getLabel(this.active_tool, this.coordPath, tmpCoords, infos);

            console.log('currentLabel:');
            console.log(currentLabel);

            switch (this.active_mode) {
                case 'new':
                    //deselect all previous labels
                    for (let i = 0; i < this.labels.length; i++) {
                        this.labels[i].selected = false;
                    }

                    if (this.active_tool == 'point' && currentLabel != null) {
                        this.labels.push({'label': currentLabel, 'label_class': this.active_label, 'type': this.active_tool, 'selected': true});
                        console.log('new point label');
                    } else if (this.active_tool != 'point' && this.active_overlap_mode == 'overlap') {
                        // new label
                        this.labels.push({'label': currentLabel, 'label_class': this.active_label, 'type': this.active_tool, 'selected': true});
                        console.log('new overlap label');
                    } else if (this.active_tool != 'point' && this.active_overlap_mode == 'no-overlap') {
                        // subtract all previous labels from this new path
                        for (var i = 0; i < this.labels.length; i++) {
                            let labl = this.labels[i].label;
                            if (this.active_tool == this.labels[i].type) {
                                currentLabel = PolyBool.difference(currentLabel, labl);
                            }
                        }

                        if (currentLabel.regions.length > 0) {
                            this.labels.push({ 'label': currentLabel, 'label_class': this.active_label, 'type': this.active_tool, 'selected': true });
                        }
                        console.log('new no overlap label');
                    }
                    break;
                case 'append':
                    if (this.active_overlap_mode == 'overlap') {
                        // if multiple labels selected, deselect the least recently created one
                        var labelIndex = getSelectedLabelIndex(this.labels);

                        if (labelIndex >= 0) {
                            // append to last label
                            let labl = this.labels[labelIndex].label;
                            currentLabel = PolyBool.union(currentLabel, labl);

                            this.labels[labelIndex].label = currentLabel;
                        }
                        console.log('append overlap label');
                    } else if (this.active_overlap_mode == 'no-overlap') {
                        // subtract all previous labels from this new path
                        for (var i = 0; i < this.labels.length; i++) {
                            if (!this.labels[i].selected && this.active_tool == this.labels[i].type) {
                                currentLabel = PolyBool.difference(currentLabel, this.labels[i].label);
                            }
                        }

                        // if multiple labels selected, deselect the least recently created one
                        var labelIndex = getSelectedLabelIndex(this.labels);

                        if (labelIndex >= 0) {
                            // append to last label (TODO: should append to selected labels)
                            if (this.labels.length > 0) {
                                let labl = this.labels[labelIndex].label;
                                currentLabel = PolyBool.union(currentLabel, labl);
                            }

                            if (currentLabel.regions.length > 0) {
                                this.labels[labelIndex].label = currentLabel;
                            }
                        }
                        console.log('append no overlap label');
                    }
                    break;
                case 'erase':
                    // subtract from selected label(s)
                    for (var i = 0; i < this.labels.length; i++) {
                        if (this.labels[i].selected) {
                            var newLabel = PolyBool.difference(this.labels[i].label, currentLabel);

                            if (newLabel.regions.length > 0) {
                                this.labels[i].label = newLabel;
                            }
                            console.log('erase label');
                        }
                    }
                    break;
                default:
                    console.error('Undefined tool mode:', this.active_mode, this.active_overlap_mode);
            }

            this.coordPath = [];

            drawAllLabels(this, this.labels, this.multiplier);
        },

        clearCanvas: function() {
            this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
            this.labels = [];
            this.labels_redo = [];
            this.edited = true;
        },

        clearLiveCanvas: function() {
            this.ctx_live.clearRect(0, 0, this.ctx_live.canvas.width, this.ctx_live.canvas.height);
        },

        validateResponse: function (response) {
            if (!response.ok) {
                console.log('error displaying image:', response.statusText);
            }
            return response;
        },

        readResponseAsBlob: function (response) {
            this.responseAsBlob = response.blob();
            return this.responseAsBlob;
        },

        setCanvasSize: function (c, width, height, padX, padY) {
            c.width = width + padX * 2;
            c.height = height + padX * 2;
            c.style.width = width + padX * 2 + 'px';
            c.style.height = height + padX * 2 + 'px';
        },

        showImage: function (responseAsBlob) {
            let canvas_live = document.getElementById("canvas-live");
            let canvas_fg = document.getElementById("canvas-fg");
            let canvas_bg = document.getElementById("canvas-bg");
            let ctx2 = canvas_bg.getContext("2d");

            this.responseAsBlob = responseAsBlob;

            let img = new Image();
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                //size image according to multiplier (for zooming)
                img.width = img.width*vm.multiplier;
                img.height = img.height*vm.multiplier;
                
                vm.setCanvasSize(canvas_fg, img.width, img.height, vm.padX, vm.padY);
                vm.setCanvasSize(canvas_bg, img.width, img.height, vm.padX, vm.padY);
                vm.setCanvasSize(canvas_live, img.width, img.height, vm.padX, vm.padY);
                // add shadow
                ctx2.shadowBlur = 10;
                ctx2.shadowColor = "hsla(2, 0%, 0%, 0.46)";

                //console.log(img)

                ctx2.drawImage(img, vm.padX, vm.padY, img.width, img.height);

                // apply brightness and contrast adjustments

                function adjustImageContrast(imgData, contrast){  //input range [-100..100]
                    var d = imgData.data;
                    contrast = (contrast / 100) + 1;  //convert to decimal & shift range: [0..2] 
                    var intercept = 128 * (1 - contrast);
                    for(var i = 0; i < d.length; i += 4) {   //r,g,b,a
                        d[i] = d[i]*contrast + intercept;
                        d[i+1] = d[i+1]*contrast + intercept;
                        d[i+2] = d[i+2]*contrast + intercept;
                    }
                    return imgData;
                }

                function adjustImageBrightness(imgData, brightness){  //input range [-100..100]
                    var d = imgData.data;
                    for (var i = 0; i < d.length; i += 4) {
                        d[i] += brightness;
                        d[i+1] += brightness;
                        d[i+2] += brightness;
                    }
                    return imgData;
                }
                
                var imgData = ctx2.getImageData(vm.padX, vm.padY, img.width, img.height);

                var imgDataAdjusted = adjustImageContrast(imgData, vm.contrast * 100);
                var imgDataAdjusted = adjustImageBrightness(imgDataAdjusted, vm.brightness * 100);

                ctx2.putImageData(imgDataAdjusted, vm.padX, vm.padY);

                // add checkerboard pattern around image

                vm.draw_pattern(img.width, img.height);

                // redraw labels

                drawAllLabels(vm, vm.labels, vm.multiplier);
            }
            img.src = imgUrl;
        },

        fetchAndDisplayImage: function (pathToResource) {

            console.log('fetching im')
            
            // let access_token = localStorage.getItem("s3_access_token");

            fetch(pathToResource)
                .then(this.validateResponse)
                .then(this.readResponseAsBlob)
                .then(this.showImage)
                .catch(function(error) {
                    console.log('error fetching and displaying image:', error);
                });
        },

        draw_pattern: function(width, height) {
            // draw background pattern

            let canvas_pattern = document.getElementById("canvas-pattern");
            let ctx_pattern = canvas_pattern.getContext("2d");    
            this.setCanvasSize(canvas_pattern, width, height, this.padX, this.padY);

            var vm = this;

            var img_pattern = new Image();

            function drawPattern() {
                ctx_pattern.fillStyle = ctx_pattern.createPattern(img_pattern, 'repeat');
                ctx_pattern.fillRect(0, 0, width + vm.padX*2, height + vm.padY*2);
            }

            img_pattern.src = '../../static/canvas_bg_pattern_3.png';
            img_pattern.onload = drawPattern;
        },

        undo: function() {
            if (this.labels_undo.length > 0) {
                this.labels.push(this.labels_undo.pop());
            } else if (this.labels.length > 0) {
                this.labels_redo.push(this.labels.pop());
            }
            drawAllLabels(this, this.labels, this.multiplier);
            this.edited = true;
        },

        redo: function() {
            if (this.labels_redo.length > 0) {
                this.labels.push(this.labels_redo.pop());
            }
            drawAllLabels(this, this.labels, this.multiplier);
            this.edited = true;
        },

        delete: function() {
            this.labels_undo.push(...this.labels.filter(lab => lab.selected));
            this.labels = this.labels.filter(lab => !lab.selected);
            drawAllLabels(this, this.labels, this.multiplier);
            this.edited = true;
        },
        
        deselect: function() {
            for (let i = 0; i < this.labels.length; i++) {
                this.labels[i].selected = false;
            }
            drawAllLabels(this, this.labels, this.multiplier);
            this.edited = true;
        },

        resize_canvas: function(mult) {
            console.log('resizing image...')
            this.showImage(this.responseAsBlob);
            //drawAllLabels(this, this.labels, this.multiplier);
        },
    },
}
</script>


<style>
.arrow-style {
    float: left;
    width: fit-content;
    height: fit-content;
}

.canvas-section div { padding-top: 2em }
.image-not-found { position:absolute; 
                   left: 0; 
                   text-align: center;
                   transform: translate(0, 300%); 
                   width: 100%; 
                   z-index: 4 }
</style>
