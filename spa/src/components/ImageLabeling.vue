<template>
    <div id="image_labeling" class="container" > <!-- @keydown="something_in_your_methods" tabindex="0"> -->
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
    data: function() {
        return {
            // TODO: store selected label task here, compute list of labels and disable/set drawing modes as specified in the label task
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            previous_tool: undefined,
            previous_mode: undefined,
            labels: [{"label_class": "Rock", "color": [255, 0, 0]}, 
                     {"label_class": "Belt", "color": [0, 255, 0]}, 
                     {"label_class": "Other", "color": [0, 0, 255]}],
            active_label: undefined,
            stroke_slider_value: "2",
            opacity_slider_value: "50",
            isDrawing: false,
            polygons: [],
            currentPath: [],
            polygons_redo: [],
            polygons_undo: [],
            padX: 80,
            padY: 80,
            el: undefined,
            el2: undefined,
            ctx: undefined,
            ctx_bg: undefined,
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
        label_colours: function() {
            var d = {};

            for (var i = 0; i < this.labels.length; i++) {
                d[this.labels[i]['label_class']] = this.labels[i]['color'];
            }
            return d;
        }
    },
    created: function () {
        // initialise active label to the first label in the set
        this.active_label = this.labels[0].label_class;
        console.log(this.labels[0].label_class)

        // console.log("console.log(store.state.count):", this.$store.state.count)
    },
    beforeMount() {
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);
    },
    mounted() {
        this.el = document.getElementById('canvas-fg');
        this.el2 = document.getElementById('canvas-bg');
        this.ctx = this.el.getContext('2d');
        this.ctx_bg = this.el2.getContext('2d');

        this.ctx.lineWidth = this.stroke_thickness;
        this.ctx.fillStyle = this.setColour(this.label_colours[this.active_label], this.opacity);

        // console.log(this.el, this.el2, this.ctx, this.ctx_bg)
    },
    beforeDestroy () {
        window.removeEventListener('keydown', this.keyDownHandler);
        window.removeEventListener('keyup', this.keyUpHandler);
    },
    watch: {
        stroke_thickness: function () {
            // this.ctx.lineWidth = this.stroke_thickness;
            this.drawAllPolygons(this.ctx, this.polygons);
        },
        use_stroke: function () {
            // this.ctx.lineWidth = this.stroke_thickness;
            this.drawAllPolygons(this.ctx, this.polygons);
        },
        opacity: function () {
            // this.ctx.lineWidth = this.stroke_thickness;
            this.drawAllPolygons(this.ctx, this.polygons);
        }
        // active_tool: function (newActiveTool, oldActiveTool) {
        //     this.previous_tool = oldActiveTool;
        // },
        // active_mode: function (newActiveMode, oldActiveMode) {
        //     this.previous_mode = oldActiveMode;
        // }
        // ctx.lineWidth: stroke_thickness_slider.value;
        // this.ctx.fillStyle = setColour(colours[active_label], opacity);
    },
    methods: {
        keyDownHandler: function(e) {
            // console.log("key:", e.code)
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
            else if (e.code === "KeyA") {
                // fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/1');
                this.clearCanvas();
            }
            else if (e.code === "KeyB") {
                // fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/2');
                this.clearCanvas();
            }
            else if (e.code === "KeyC") {
                // fetchAndDisplayImage('http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/3');
                this.clearCanvas();
            }
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
                console.log(e.code);
            }

            e.stopPropagation();
            e.preventDefault();
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
                console.log(e.code);
            }

            e.stopPropagation();
            e.preventDefault();
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

        formatColour: function (rgb, alpha) {
            return 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',' + alpha + ')';
        },

        setColour: function (rgb, alpha) {
            this.ctx.fillStyle = this.formatColour(rgb, alpha);
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
            this.setColour(this.label_colours[polygon.label], this.opacity);
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