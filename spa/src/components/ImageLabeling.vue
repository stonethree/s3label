<template>
    <div id="image_labeling" class="container" >
        <div id="drawingtools">
            <div class="row">
                <div id="tools" class="col border-right">
                    <span>Tools</span>
                    <form id="tools_form">
                        <input type="radio" class="radio-button" name="tool" value="freehand" v-model="active_tool"> Freehand
                        <br>
                        <input type="radio" class="radio-button" name="tool" value="polygon" v-model="active_tool"> Polygon
                        <br>
                        <input type="radio" class="radio-button" name="tool" value="select" v-model="active_tool"> Select
                    </form>
                </div>
                <div id="tool_modes" class="col border-right">
                    <span>Modes</span>
                    <form id="mode_form">
                        <input type="radio" class="radio-button" name="mode" value="new" v-model="active_mode"> New
                        <br>
                        <input type="radio" class="radio-button" name="mode" value="append" v-model="active_mode"> Append
                        <br>
                        <input type="radio" class="radio-button" name="mode" value="erase" v-model="active_mode"> Erase
                    </form>
                </div>
                <div id="choose_overlap" class="col border-right">
                    <span>Overlap Mode</span>
                    <form>
                        <input type="radio" class="radio-button" name="overlap_mode" value="overlap" v-model="active_overlap_mode"> Overlapping
                        <br>
                        <input type="radio" class="radio-button" name="overlap_mode" value="no-overlap" v-model="active_overlap_mode"> Non-overlapping
                    </form>
                </div>
                <div id="semantic_labels" class="col border-right">
                    <span>Semantic Labels</span>
                    <form>
                        <div v-for="label in labels" :key="label.label_class">
                            <input type="radio" class="radio-button" name="semantic_label" :value="label.label_class" v-model="active_label"> {{ label.label_class }} <br>
                        </div>
                    </form>
                </div>
                <div id="graphics_settings" class="col">
                    <div id="stroke_slider_container">
                        <span>Stroke thickness</span>
                        <input id="stroke_thickness_slider" type="range" min="0" max="10" class="slider" v-model="stroke_slider_value">
                    </div>
                    <div id="opacity_slider_container">
                        <span>Opacity</span>
                        <input id="opacity_slider" type="range" min="0" max="100" class="slider" v-model="opacity_slider_value">
                    </div>
                </div>
                <div id="clear_canvas_container" class="col">
                    <button type="submit" @click="clearCanvas">Clear canvas</button>
                </div>
            </div>
        </div>

        <div >
        <div id="canvasesdiv" style="position:relative;" @mousedown="mouseDownHandler" @mouseup="mouseUpHandler" @mousemove="mouseMoveHandler">
            <canvas id="canvas-fg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;" v-draw-on-canvas="polygons"></canvas>
            <canvas id="canvas-bg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
        </div>
        </div>
    </div>
</template>

<script>

import { mapGetters } from 'vuex'
import axios from "axios";

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

// polygon operations

var PolyBool = require('polybooljs');

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

export default {
    name: 'image_labeling',
    props: ['input_data_id_start'],
    data: function() {
        return {
            // TODO: store selected label task here, compute list of labels and disable/set drawing modes as specified in the label task
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            previous_tool: undefined,
            previous_mode: undefined,
            active_label: null,
            stroke_slider_value: "2",
            opacity_slider_value: "50",
            isDrawing: false,
            polygons: [],
            currentPath: [],
            polygons_redo: [],
            polygons_undo: [],
            padX: 80,
            padY: 80,
            ctx: undefined,
            ctx_bg: undefined,
            input_data_id: undefined
        };
    },
    computed: {
        stroke_thickness: function() {
            return Math.max(1, parseInt(this.stroke_slider_value));
        },
        use_stroke: function() {
            return parseInt(this.stroke_slider_value) > 0 ? true : false; 
        },
        opacity: function() {
            return parseFloat(this.opacity_slider_value) / 100.;
        },
        // ...mapGetters([
        //     'label_task',
        // ]),
        label_task: function() {
            return this.$store.getters.label_task;
        },
        labels: function() {
            if (this.label_task != undefined) {
                return JSON.parse(this.label_task.label_classes);
            }
            else {
                return undefined;
            }
        },
        label_colors: function() {
            if (this.label_task != undefined) {
                var d = {};

                for (var i = 0; i < this.labels.length; i++) {
                    d[this.labels[i].label_class] = this.extractColor(this.labels[i].color);
                }
                return d;
            }
            else {
                return null
            }

            
        }
    },
    created: function () {

        // go to label task chooser page if user has not selected a label task

        if (this.label_task == undefined) {
            this.$router.push('label_tasks');
        }
    },
    beforeMount() {
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);
    },
    mounted() {
        var el = document.getElementById('canvas-fg');
        var el2 = document.getElementById('canvas-bg');
        this.ctx = el.getContext('2d');
        this.ctx_bg = el2.getContext('2d');

        // this.ctx.lineWidth = this.stroke_thickness;
        // this.ctx.fillStyle = this.setColor(this.label_colors[this.active_label], this.opacity);

        // initialise active label to the first label in the set
        if (this.labels != undefined && this.labels.length > 0) {
            this.active_label = this.labels[0].label_class;
            console.log(this.labels[0].label_class)
        }

        // begin with specified image

        if (this.input_data_id_start != undefined) {
            this.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + this.input_data_id_start);
            this.input_data_id = this.input_data_id_start;
        }
    },
    beforeDestroy () {
        window.removeEventListener('keydown', this.keyDownHandler);
        window.removeEventListener('keyup', this.keyUpHandler);
    },
    beforeRouteLeave (to, from, next) {
        // save image labels before navigating away
        this.uploadLabeledImage(this.input_data_id);
        next()
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
            // save previous image's labels to database
            if (old_input_data_id != undefined) {
                console.log('Saving labels for this image', new_input_data_id, old_input_data_id)
                this.uploadLabeledImage(old_input_data_id);
            }

            this.clearCanvas();
            
            // when input image ID changes (i.e. new image is loaded), load latest image label from database 
            this.loadImageLabels(new_input_data_id);
        }
    },
    methods: {
        keyDownHandler: function(e) {
            console.log("key down:", e.code)
            if (e.ctrlKey && e.code === "KeyZ") {
                console.log("Undo");
                this.undo();
                this.drawAllPolygons(this.ctx, this.polygons);
            }
            else if (e.ctrlKey && e.code === "KeyY") {
                console.log("Redo");
                this.redo();
                this.drawAllPolygons(this.ctx, this.polygons);
            }
            else if (e.code === "ArrowLeft") {
                console.log('get preceding labeled image')

                let access_token = localStorage.getItem("s3_access_token");

                let config = {
                    headers: {
                    Authorization: "Bearer " + access_token
                    }
                };

                var vm = this;

                axios
                    .get("labeled_data/label_tasks/" + this.label_task.label_task_id + "?action=previous&current_input_data_id=" + this.input_data_id, config)
                    .then(function(response) {
                        if (response.data.length == 1) {
                            var preceding_data_item = response.data[0];
                            vm.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + preceding_data_item.input_data_id);
                            vm.input_data_id = preceding_data_item.input_data_id;
                        }
                    })
                    .catch(function(error) {
                    console.log(error);
                    });
            }
            else if (e.code === "ArrowRight") {
                // first try get next image that the user has already viewed/labeled, if one exists

                let access_token = localStorage.getItem("s3_access_token");

                let config = {
                    headers: {
                    Authorization: "Bearer " + access_token
                    }
                };

                var vm = this;
                var got_an_image = false;


                // check if we have an input data ID first

                if (this.input_data_id != undefined) {
                    axios
                        .get("labeled_data/label_tasks/" + this.label_task.label_task_id + "?action=next&current_input_data_id=" + this.input_data_id, config)
                        .then(function(response) {
                            if (response.data.length == 1) {
                                var next_data_item = response.data[0];
                                vm.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + next_data_item.input_data_id);
                                vm.input_data_id = next_data_item.input_data_id;
                                got_an_image = true;
                            }
                        })
                        .catch(function(error) {
                        console.log(error);
                        });
                }

                // request a fresh unlabeled image if we have already scrolled to the most recent image

                if (!got_an_image) {
                    console.log('get new unlabeled image')

                    axios
                        .get("unlabeled_images/label_tasks/" + this.label_task.label_task_id + "?shuffle=true", config)
                        .then(function(response) {
                            console.log(response.data)
                            return response.data.input_data_id;
                        })
                        .then(function(input_data_id) {
                            vm.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + input_data_id);
                            vm.input_data_id = input_data_id;
                            got_an_image = true;
                        })
                        .catch(function(error) {
                        console.log(error);
                        });
                }

                // if we have scrolled to the most recent image and no unlabeled images are available, display a message to the user

                if (!got_an_image) {
                    console.log("No more unlabeled images available!")
                }
            }
            // else if (e.code === "KeyA") {
            //     var input_data_id = 1;
            //     this.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + input_data_id);
            //     this.input_data_id = input_data_id;
            // }
            // else if (e.code === "KeyB") {
            //     var input_data_id = 2;
            //     this.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + input_data_id);
            //     this.input_data_id = input_data_id;
            // }
            // else if (e.code === "KeyC") {
            //     var input_data_id = 3;
            //     this.fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/' + input_data_id);
            //     this.input_data_id = input_data_id;
            // }
            // else if (e.code == 'KeyS') {
            //     console.log('Saving labels for this image')
            //     this.uploadLabeledImage(this.input_data_id);
            // }
            // else if (e.code == 'KeyL') {
            //     console.log('Loading labels for this image')
            //     this.loadImageLabels(this.input_data_id);
            // }
            else if (e.code === 'Delete') {
                console.log('num orig polys:', this.polygons.length, 'num redo polys:', this.polygons_redo.length)
                this.polygons_undo.push(...this.polygons.filter(poly => poly.selected));
                this.polygons = this.polygons.filter(poly => !poly.selected);
                console.log('num final polys:', this.polygons.length, 'num redo polys:', this.polygons_redo.length)
                this.drawAllPolygons(this.ctx, this.polygons);
            }
            else if (e.code === 'Escape') {
                for (let i = 0; i < this.polygons.length; i++) {
                    this.polygons[i].selected = false;
                }
                this.drawAllPolygons(this.ctx, this.polygons);
            }
            else if (e.code == 'Space') {
                if (this.previous_tool === undefined && !this.isDrawing) {
                    this.previous_tool = this.active_tool;
                    this.active_tool = 'select';
                    console.log('temp selecting (down)')
                }
            }
            else if (e.code.startsWith('Shift')) {
                if (this.previous_mode === undefined && !this.isDrawing) {
                    this.previous_mode = this.active_mode;
                    this.active_mode = 'append';
                    console.log('temp mode append (down)')
                }
            }
            else if (e.code.startsWith('Alt')) {
                if (this.previous_mode === undefined && !this.isDrawing) {
                    this.previous_mode = this.active_mode;
                    this.active_mode = 'erase';
                    console.log('temp mode erase (down)')
                }
            }
            else {
                console.log('key not found (down):', e.code);
            }

            // e.stopPropagation();
            // e.preventDefault();
        },

        keyUpHandler: function (e) {
            if (e.code === 'Space') {
                if (this.previous_tool) {
                    this.active_tool = this.previous_tool;
                    this.previous_tool = undefined;
                    console.log('temp selecting (up)')
                }
            }
            else if (e.code.startsWith('Shift')) {
                if (this.previous_mode) {
                    this.active_mode = this.previous_mode;
                    this.previous_mode = undefined;
                    console.log('temp mode append (up)')
                }
            }
            else if (e.code.startsWith('Alt')) {
                if (this.previous_mode) {
                    this.active_mode = this.previous_mode;
                    this.previous_mode = undefined;
                    console.log('temp mode erase (up)')
                }
            }
            else {
                console.log('key not found (up):', e.code);
            }

            // e.stopPropagation();
            // e.preventDefault();
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

        extractColor: function (rgb_string) {
            // takes a string of format
            var rgb = JSON.parse(rgb_string)

            if (rgb.length == 3) {
                return rgb;
            }
            else {
                throw TypeError('Color string must have 3 RGB elements specified');
            }
        },

        formatColor: function (rgb, alpha) {
            return 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',' + alpha + ')';
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

        logError: function (error) {
            console.log('Looks like there was a problem: \n', error);
        },

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
            console.log('c '+ c.width + ', ' + c.height, padX, padY);
        },

        showImage: function (responseAsBlob) {
            let canvas_fg = document.getElementById("canvas-fg");
            let canvas_bg = document.getElementById("canvas-bg");

            // let ctx = canvas_fg.getContext("2d");
            let ctx2 = canvas_bg.getContext("2d");    

            let img = new Image();
            console.log(responseAsBlob)
            let imgUrl = URL.createObjectURL(responseAsBlob); //.data);
            // let imgUrl = responseAsBlob;

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
                .catch(this.logError);
            
            // fetch(pathToResource, {
            //       headers: new Headers({ 'Authorization': "Bearer " + access_token })
            //       })
            //     .then(this.validateResponse)
            //     .then(this.readResponseAsBlob)
            //     .then(this.showImage)
            //     .catch(this.logError);

            // let config = {
            //     headers: {
            //     Authorization: "Bearer " + access_token
            //     },
            //     responseType: 'arraybuffer'
            // };

            // axios
            //     .get(pathToResource, config)
            //     // .then(this.validateResponse)
            //     // .then(this.readResponseAsBlob)
            //     .then(response => new Buffer(response.data, 'binary').toString('base64'))
            //     .then(this.showImage)
            //     .catch(this.logError);
        },

        uploadLabeledImage: function (input_data_id) {

            console.log('uploading label with label task ID', this.label_task.label_task_id, 'and input data ID', input_data_id)

            var data = {label_serialised: this.polygons}

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
            .post("label_history/label_tasks/" + this.label_task.label_task_id + "/input_data/" + input_data_id, data, config)
            .then(function(response) {
                console.log(response)
            })
            .catch(function(error) {
            console.log(error);
            });
        },

        loadImageLabels: function (input_data_id) {

            console.log('getting image labels with label task ID', this.label_task.label_task_id, 'and input data ID', input_data_id)

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            var vm = this;

            axios
            .get("labels/input_data/" + input_data_id + "/label_tasks/" + this.label_task.label_task_id, config)
            .then(function(response) {
                console.log(response.data)

                if (response.data.length == 1) {
                    console.log("Label found for this image: attempting to apply it in the view")
                    var label = response.data[0];

                    // check label format is correct

                    console.log(label)

                    var polygons = JSON.parse(label.label_serialised);

                    if (polygons.length > 0 && polygons[0].polygon != undefined) {
                        console.log('Applied serialised label to image')
                        vm.polygons = polygons;
                        vm.drawAllPolygons(vm.ctx, vm.polygons);
                    }
                    else {
                        console.log('Serialised label has wrong format:', polygons)
                    }
                }
                else if (response.data.length == 0) {
                    console.log("No label found for this image")
                }
                else {
                    console.log("Error: expected at most one label for this image!")
                }
            })
            .catch(function(error) {
            console.log(error);
            });
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
/* #image_labeling {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>