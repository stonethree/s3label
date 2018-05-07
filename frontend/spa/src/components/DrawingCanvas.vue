<template>
    <div class="canvas-section" style="position:static; display: inline;">
        <div id="labelstatusdiv" style="position:relative;">
            <label-status v-bind:label-id="label_id" v-bind:user-completed-toggle="label_status_toggler.user_complete" style="width:500px;height:350px; position:absolute; left:50%; top:-2em; transform: translate(-50%, 0);"></label-status>
        </div>
        <div id="canvasesdiv" style="position:relative;" @mousedown="mouseDownHandler" @mouseup="mouseUpHandler" @mousemove="mouseMoveHandler">
            <!-- <div style="position:absolute; display: inline;">
                <p>testing123</p>
                </div> -->
            <canvas id="canvas-fg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 3; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <canvas id="canvas-bg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
            <canvas id="canvas-pattern" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:50%; top:0px; transform: translate(-50%, 0);"></canvas>
        </div>
    </div>
</template>

<script>

import { mapGetters } from 'vuex'

import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

// polygon operations

var PolyBool = require('polybooljs');
import { convertPolygonToPaths, 
         convertPathToPolygon, 
         isPointInPolygon, 
         getSelectedPolygonIndex, 
         isPolygonLargeEnough } from '../../static/PolygonOperations'

import LabelStatus from './LabelStatus'
import { extractColor, formatColor } from '../../static/color_utilities'

import { uploadLabels,
         loadLabels,
         getLabelId } from '../../static/label_loading'


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
        clear_canvas_event: {
            required: false,
            type: Boolean,
            default: false
        },
    },
    data: function() {
        return {
            isDrawing: false,
            currentPath: [],
            padX: 80,
            padY: 80,
            ctx: undefined,
            ctx_bg: undefined,
            label_status_toggler: {user_complete: false},
            polygons: [],
            polygons_redo: [],
            polygons_undo: [],
            label_id: undefined
        };
    },
    components: {
        LabelStatus,
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_colors'
        ]),
        ...mapGetters('user_login', [
            'user_id'
        ]),
    },
    mounted() {
        var el = document.getElementById('canvas-fg');
        var el2 = document.getElementById('canvas-bg');
        this.ctx = el.getContext('2d');
        this.ctx_bg = el2.getContext('2d');

        console.log('------ mounted page')

        // if an image ID is specified, get its corresponding label ID and load that image

        if (this.input_data_id != undefined) {
            console.group('input_data_id: ' + this.input_data_id);
            
            this.open_image();
        }
        else {
            this.draw_image_unavailable_placeholder()
        }
    },
    watch: {
        stroke_thickness: function () {
            this.drawAllPolygons(this.ctx, this.polygons);
        },
        use_stroke: function () {
            this.drawAllPolygons(this.ctx, this.polygons);
        },
        opacity: function () {
            this.drawAllPolygons(this.ctx, this.polygons);
        },
        input_data_id: function (new_input_data_id, old_input_data_id) {
            console.log('switching image...')
            this.switch_image(old_input_data_id, new_input_data_id);
        },

        polygons: function() {
            this.drawAllPolygons(this.ctx, this.polygons);
        },

        clear_canvas_event: function() {
            this.clearCanvas();
            console.log('clear canvas toggled')
        }
    },
    methods: {
        save_labels: async function() {
            // save image labels before navigating away. Called by parent component, since we cannot use vue-router's beforeRouteLeave() function within a subcomponent.

            var vm = this;

            if (this.input_data_id != undefined) {
                await uploadLabels(this.input_data_id, this.label_task_id, this.polygons)
                    .then(function(response) {
                        console.log('test8-B')
                        if (vm.polygons.length > 0) {
                            console.log('SAVED LABELS SUCCESSFULLY (LEAVING PAGE)', vm.polygons)
                        }
                        else {
                            console.warn('SAVED LABELS SUCCESSFULLY, but length 0 (LEAVING PAGE):', vm.polygons)
                        }
                    })
            }
            else {
                throw Error('could not save image before leaving page!')
            }

            console.groupEnd();
        },

        open_image: async function() {
            // display an image and load corresponding labels if any exist

            var vm = this;
            console.log('test1-A')
            await this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
            console.log('test2-A')

            await getLabelId(this.label_task_id, this.input_data_id, this.user_id)
                .then(function(label_id) {
                        vm.label_id = label_id;
                        console.log('test3-A')
                        console.log('GOT LABEL ID SUCCESSFULLY', label_id)
                    })
                    .catch(function(error) {
                        throw Error('error getting label ID:', error, vm.label_task_id, vm.input_data_id, vm.user_id);
                    });

            console.log('test4-A')

            // load latest image labels for this image from database 

            if (this.input_data_id != undefined) {
                await loadLabels(this.input_data_id, this.label_task_id)
                    .then(function(polygons) {
                        vm.polygons = polygons;
                        console.log('test5-A')
                        if (vm.polygons.length > 0) {
                            console.log('SAVED LABELS SUCCESSFULLY', vm.polygons)
                        }
                        else {
                            console.warn('SAVED LABELS SUCCESSFULLY, but length 0:', vm.polygons)
                        }
                    })
            }
        },

        switch_image: async function(old_input_data_id, new_input_data_id) {

            // save previous image's labels to database

            if (old_input_data_id != undefined) {
                var vm = this;
                await uploadLabels(old_input_data_id, this.label_task_id, this.polygons)
                    .then(function(response) {
                        console.log('test8')
                        if (vm.polygons.length > 0) {
                            console.log('SAVED LABELS SUCCESSFULLY', vm.polygons)
                        }
                        else {
                            console.warn('SAVED LABELS SUCCESSFULLY, but length 0:', vm.polygons)
                        }
                    })
                    .catch(function(error) {
                        throw Error('could not upload labels:', old_input_data_id, vm.label_task_id, vm.polygons)
                    });
            }

            console.log('test9')

            console.log('CLEARING CANVAS: SWITCHING TO NEW IMAGE')

            await this.clearCanvas();

            console.groupEnd();

            console.group('input_data_id: ' + new_input_data_id);

            console.log('test1')

            if (new_input_data_id != undefined) {
                await this.fetchAndDisplayImage(baseUrl + '/input_images/' + new_input_data_id);

                console.log('test2')

                // get the label ID corresponding to this input data item, user and label task

                var vm = this;

                await getLabelId(this.label_task_id, new_input_data_id, this.user_id)
                    .then(function(label_id) {
                        console.log('test3')
                        vm.label_id = label_id;
                        console.log('GOT LABEL ID SUCCESSFULLY', label_id)
                    })
                    .catch(function(error) {
                        throw Error('error getting label ID:', error, vm.label_task_id, new_input_data_id, vm.user_id);
                    });

                // load latest image labels for this image from database 

                console.log('test4')

                await loadLabels(new_input_data_id, this.label_task_id)
                    .then(function(polygons) {
                        // if (checkLabelFormatValid) {
                            console.log('test5')
                            vm.polygons = polygons;
                            console.log('LOADED LABELS SUCCESSFULLY', vm.polygons)
                            vm.drawAllPolygons(vm.ctx, vm.polygons);
                        // }
                        // else {
                        //     throw Error('could not load labels: wrong format!!!!!' + polygons)
                        // }
                    })
                    // .catch(function(error) {
                    //     console.log('error getting label ID:', error);
                    // });
            }
            else {
                this.draw_image_unavailable_placeholder();
            }
        },

        draw_image_unavailable_placeholder: function() {
            // draw a placeholder image to the canvas and state to the user that no unlabeled images found

            let canvas_bg = document.getElementById("canvas-bg");
            let canvas_fg = document.getElementById("canvas-fg");
            let canvas_pattern = document.getElementById("canvas-pattern");
            let ctx2 = canvas_bg.getContext("2d");  

            let w = 600;
            let h = 400;

            this.setCanvasSize(canvas_bg, w, h, this.padX, this.padY);
            this.setCanvasSize(canvas_fg, w, h, this.padX, this.padY);

            ctx2.fillStyle = "hsl(25, 80%, 80%)";
            ctx2.fillRect(this.padX, this.padY, w, h);
            ctx2.fillStyle = "hsl(25, 80%, 10%)";
            ctx2.fillText("No unlabeled images available for this label task", 200, 200);

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

            if (this.active_tool == 'freehand') {
                this.polygons_redo = [];
                this.isDrawing = true;
                this.ctx.lineJoin = this.ctx.lineCap = 'round';
                this.ctx.beginPath();
                this.ctx.moveTo(coords.x, coords.y);
                this.currentPath.push([coords.x, coords.y]);
            }
            if (this.active_tool == 'polygon') {
                if (!this.isDrawing) {
                    this.polygons_redo = [];
                    this.isDrawing = true;
                    this.ctx.lineJoin = this.ctx.lineCap = 'round';
                    this.ctx.beginPath();
                    this.ctx.moveTo(coords.x, coords.y);
                    this.currentPath.push([coords.x, coords.y]);
                }
                else {
                    var lastPoint = this.currentPath[this.currentPath.length - 1];
                    if (Math.abs(coords.x - lastPoint[0]) < 2 && Math.abs(coords.y - lastPoint[1]) < 2) {
                        // close and finish drawing path if same point clicked twice
                        this.currentPath.push(this.currentPath[0]);
                        this.processPolygon();
                    }
                    else {
                        // add point to current path
                        this.ctx.lineTo(coords.x, coords.y);
                        this.ctx.stroke();
                        this.currentPath.push([coords.x, coords.y]);
                    }
                }
            }
            else if (this.active_tool == 'select') {
                // check which polygons the point lies within

                for (var jjj = 0; jjj < this.polygons.length; jjj++) {
                    var currentPolygon = this.polygons[jjj];
                    var selected = false;

                    for (var iii = 0; iii < currentPolygon.polygon.regions.length; iii++) {
                        var xs = currentPolygon.polygon.regions[iii].map(p => p[0]);
                        var ys = currentPolygon.polygon.regions[iii].map(p => p[1]);

                        if (isPointInPolygon(coords.x, coords.y, xs, ys)) {
                            selected = true;
                        }
                    }

                    currentPolygon.selected = selected;
                }

                this.drawAllPolygons(this.ctx, this.polygons);
            }
        },

        mouseMoveHandler: function (e) {
            if (this.active_tool == 'freehand') {
                if (this.isDrawing) {
                    var coords = this.getMousePos(this.ctx.canvas, e);
                    if (coords.x == undefined || coords.y == undefined) {
                        console.log("coords undef:" + coords);
                    }
                    this.ctx.lineTo(coords.x, coords.y);
                    this.ctx.stroke();
                    this.currentPath.push([coords.x, coords.y]);
                }
            }
        },

        mouseUpHandler: function () {
            if (this.active_tool == 'freehand' && this.isDrawing) {
                this.processPolygon();
            }
        },

        processPolygon: function () {
            this.isDrawing = false;

            this.ctx.closePath();
            if (this.use_stroke) {
                this.ctx.stroke();
            }
            this.ctx.fill();

            // do not add polygon if it has zero area
            if (!isPolygonLargeEnough(this.currentPath)) {
                console.log('polygon too small! discarding it')

                this.currentPath = [];
                this.drawAllPolygons(this.ctx, this.polygons);
                return;
            }

            if (this.active_mode == 'new') {
                // deselect all previous polygons

                for (let i = 0; i < this.polygons.length; i++) {
                    this.polygons[i].selected = false;
                }
            }

            let currentPolygon = convertPathToPolygon(this.currentPath);

            if (this.active_mode == 'new' && this.active_overlap_mode == 'overlap') {
                // new polygon

                if (this.currentPolygon.regions.length > 0) {
                    this.polygons.push({ 'polygon': currentPolygon, 'label': this.active_label, 'type': this.active_tool, 'selected': true });
                }
                console.log('new overlap poly');
            }
            else if (this.active_mode == 'new' && this.active_overlap_mode == 'no-overlap') {
                // subtract all previous polygons from this new path
                for (var i = 0; i < this.polygons.length; i++) {
                    let poly = this.polygons[i].polygon;
                    currentPolygon = PolyBool.difference(currentPolygon, poly);
                }

                if (currentPolygon.regions.length > 0) {
                    this.polygons.push({ 'polygon': currentPolygon, 'label': this.active_label, 'type': this.active_tool, 'selected': true });
                }
                console.log('new no overlap poly');
            }
            else if (this.active_mode == 'append' && this.active_overlap_mode == 'overlap') {
                // if multiple polygons selected, deselect the least recently created one
                var polyIndex = getSelectedPolygonIndex(this.polygons);

                if (polyIndex >= 0) {
                    // append to last polygon
                    let poly = this.polygons[polyIndex].polygon;
                    currentPolygon = PolyBool.union(currentPolygon, poly);

                    this.polygons[polyIndex].polygon = currentPolygon;
                }
                console.log('append overlap poly');
            }
            else if (this.active_mode == 'append' && this.active_overlap_mode == 'no-overlap') {
                // subtract all previous polygons from this new path
                for (var i = 0; i < this.polygons.length; i++) {
                    if (!this.polygons[i].selected) {
                        currentPolygon = PolyBool.difference(currentPolygon, this.polygons[i].polygon);
                    }
                }

                // if multiple polygons selected, deselect the least recently created one
                var polyIndex = getSelectedPolygonIndex(this.polygons);

                if (polyIndex >= 0) {
                    // append to last polygon (TODO: should append to selected polygons)
                    if (this.polygons.length > 0) {
                        let poly = this.polygons[polyIndex].polygon;
                        currentPolygon = PolyBool.union(currentPolygon, poly);
                    }

                    if (currentPolygon.regions.length > 0) {
                        this.polygons[polyIndex].polygon = currentPolygon;
                    }
                }
                console.log('append no overlap poly');
            }
            else if (this.active_mode == 'erase') {
                // subtract from selected polygon(s)

                for (var i = 0; i < this.polygons.length; i++) {
                    if (this.polygons[i].selected) {
                        var newPolygon = PolyBool.difference(this.polygons[i].polygon, currentPolygon);

                        if (newPolygon.regions.length > 0) {
                            this.polygons[i].polygon = newPolygon;
                        }
                        console.log('erase poly');
                    }
                }
            }
            else {
                console.error('Undefined tool mode:', this.active_mode, this.active_overlap_mode);
            }

            this.currentPath = [];

            this.drawAllPolygons(this.ctx, this.polygons);
        },

        setColor: function (rgb, alpha) {
            this.ctx.fillStyle = formatColor(rgb, alpha);
        },

        clearCanvas: function() {
            this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
            this.polygons = [];
            this.polygons_redo = [];
            console.log('(CLEARING CANVAS)')
        },

        drawAllPolygons: function (context, polygon_list) {
            context.lineWidth = this.stroke_thickness;
            context.clearRect(0, 0, context.canvas.width, context.canvas.height);

            for (let i = 0; i < polygon_list.length; i++) {
                this.drawPolygon(context, polygon_list[i]);
            }
        },

        drawPolygon: function (context, polygon) {
            this.setColor(this.label_colors[polygon.label], this.opacity);
            let paths_to_draw = convertPolygonToPaths(polygon.polygon);

            if (polygon.selected) {
                // draw selected polygon

                var currentStrokeStyle = context.strokeStyle;
                context.strokeStyle = "#FF0000";
                context.setLineDash([4, 4]);

                for (let j = 0; j < paths_to_draw.length; j++) {
                    this.drawPath(context, paths_to_draw[j]);
                }

                context.strokeStyle = currentStrokeStyle;
                context.setLineDash([]);
            }
            else {
                // draw unselected polygon

                for (let j = 0; j < paths_to_draw.length; j++) {
                    this.drawPath(context, paths_to_draw[j]);
                }
            }
        },

        drawPath: function (context, path) {

            let w = context.canvas.width;
            let h = context.canvas.height;

            context.beginPath();
            context.moveTo(Math.max(this.padX, Math.min(path[0][0], w - this.padX)),
                Math.max(this.padY, Math.min(path[0][1], h - this.padY)));

            for (let i = 1; i < path.length; i++) {
                context.lineTo(Math.max(this.padX, Math.min(path[i][0], w - this.padX)),
                    Math.max(this.padY, Math.min(path[i][1], h - this.padY)));
            }

            context.closePath();
            if (this.use_stroke) {
                context.stroke();
            }
            context.fill();
        },

        // image displaying functions

        validateResponse: function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response;
        },

        readResponseAsBlob: function (response) {
            return response.blob();
        },

        setCanvasSize: function (c, width, height, padX, padY) {
            c.width = width + padX * 2;
            c.height = height + padX * 2;
            c.style.width = width + padX * 2 + 'px';
            c.style.height = height + padX * 2 + 'px';
        },

        showImage: function (responseAsBlob) {
            let canvas_fg = document.getElementById("canvas-fg");
            let canvas_bg = document.getElementById("canvas-bg");
            let ctx2 = canvas_bg.getContext("2d");

            let img = new Image();
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                vm.setCanvasSize(canvas_fg, img.width, img.height, vm.padX, vm.padY);
                vm.setCanvasSize(canvas_bg, img.width, img.height, vm.padX, vm.padY);

                // add shadow

                ctx2.shadowBlur = 10;
                ctx2.shadowColor = "hsla(2, 0%, 0%, 0.46)";

                ctx2.drawImage(img, vm.padX, vm.padY);

                // add checkerboard pattern around image

                vm.draw_pattern(img.width, img.height);
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
        }
    },

    directives: {
        drawOnCanvas: function(canvasElement, binding) {
            // // Get canvas context
            // var ctx = canvasElement.getContext("2d");
            // // Clear the canvas
            // ctx.clearRect(0, 0, 300, 150);
            // // Insert stuff into canvas
            // ctx.fillStyle = "black";
            // ctx.font = "20px Georgia";
            // ctx.fillText(binding.value, 10, 50);
            // console.log("length: ", binding.value.length, binding.value)
        }
    },
}
</script>


<style>
.canvas-section div { padding-top: 2em }
/* #drawing_canvas {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>