<template>
<!-- TODO need to dynamically set Label ID!!! -->
        <div class="canvas-section">
            <!-- <label-status v-bind:label-id="1" v-bind:user-completed-toggle="label_status_toggler.user_complete"></label-status> -->
            <!-- <label-status v-bind:user-completed-toggle="label_status_toggler.user_complete"></label-status> -->
            <div id="canvasesdiv" style="position:relative;" @mousedown="mouseDownHandler" @mouseup="mouseUpHandler" @mousemove="mouseMoveHandler">
                <canvas id="canvas-fg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;" v-draw-on-canvas="polygons"></canvas>
                <canvas id="canvas-bg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
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
import {convertPolygonToPaths, convertPathToPolygon, isPointInPolygon, getSelectedPolygonIndex, isPolygonLargeEnough } from '../../static/PolygonOperations'

import LabelStatus from './LabelStatus'
import { extractColor, formatColor } from '../../static/color_utilities'


export default {
    name: 'drawing_canvas',
    data: function() {
        return {
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            active_label: null,
            isDrawing: false,
            polygons: [],
            currentPath: [],
            polygons_redo: [],
            polygons_undo: [],
            padX: 80,
            padY: 80,
            ctx: undefined,
            ctx_bg: undefined,
            label_status_toggler: {user_complete: false},
        };
    },
    components: {
        LabelStatus,
    },
    computed: {
        ...mapGetters('image_labeling', [
            'input_data_id',
            'label_id'
        ]),
        // stroke_thickness: function() {
        //     return Math.max(1, parseInt(this.stroke_slider_value));
        // },
        // use_stroke: function() {
        //     return parseInt(this.stroke_slider_value) > 0 ? true : false; 
        // },
        // opacity: function() {
        //     return parseFloat(this.opacity_slider_value) / 100.;
        // },
        // label_task: function() {
        //     return this.$store.getters.label_task;
        // },
        // labels: function() {
        //     if (this.label_task != undefined) {
        //         return JSON.parse(this.label_task.label_classes);
        //     }
        //     else {
        //         return undefined;
        //     }
        // },
        // label_colors: function() {
        //     if (this.labels != undefined) {
        //         var d = {};

        //         for (var i = 0; i < this.labels.length; i++) {
        //             d[this.labels[i].label_class] = this.extractColor(this.labels[i].color);
        //         }
        //         return d;
        //     }
        //     else {
        //         return undefined
        //     }
        // },
    },
    mounted() {
        var el = document.getElementById('canvas-fg');
        var el2 = document.getElementById('canvas-bg');
        this.ctx = el.getContext('2d');
        this.ctx_bg = el2.getContext('2d');

        // if an image ID is specified, load that image

        if (this.input_data_id != undefined) {
            this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
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
            // // save previous image's labels to database
            // if (old_input_data_id != undefined) {
            //     this.uploadLabeledImage(old_input_data_id);
            // }

            // this.clearCanvas();
            
            // when input image ID changes (i.e. new image is loaded), load latest image label from database 
            // if (new_input_data_id != undefined) {
            //     this.loadImageLabels(new_input_data_id);
            // }

            // get the label ID corresponding to this input data item, user and label task

            // this.get_label_id(this.label_task_id, new_input_data_id, this.user_id)


            if (this.input_data_id != undefined) {
                this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
            }
            else {
                this.draw_image_unavailable_placeholder()
            }
        },
    },
    methods: {
        draw_image_unavailable_placeholder: function() {
            // draw a placeholder image to the canvas and state to the user that no unlabeled images found

            let canvas_bg = document.getElementById("canvas-bg");
            let canvas_fg = document.getElementById("canvas-fg");
            let ctx2 = canvas_bg.getContext("2d");  

            let w = 600;
            let h = 400;

            this.setCanvasSize(canvas_bg, w, h, this.padX, this.padY);
            this.setCanvasSize(canvas_fg, w, h, this.padX, this.padY);

            ctx2.fillStyle = "hsl(25, 80%, 80%)";
            ctx2.fillRect(this.padX, this.padY, w, h);
            ctx2.fillStyle = "hsl(25, 80%, 10%)";
            ctx2.fillText("No unlabeled images available for this label task", 200, 200);
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
            console.log("this.active_label:", this.active_label)
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

        undo: function() {
            if (this.polygons_undo.length > 0) {
                this.polygons.push(this.polygons_undo.pop());
            }
            else if (this.polygons.length > 0) {
                this.polygons_redo.push(this.polygons.pop());
            }
        },

        redo: function() {
            if (this.polygons_redo.length > 0) {
                this.polygons.push(this.polygons_redo.pop());
            }
        },

        setColor: function (rgb, alpha) {
            this.ctx.fillStyle = this.formatColor(rgb, alpha);
        },

        clearCanvas: function() {
            this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
            this.polygons = [];
            this.polygons_redo = [];
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
                ctx2.drawImage(img, vm.padX, vm.padY);
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
/* .canvas-section div { padding-top: 2em } */
/* #drawing_canvas {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>