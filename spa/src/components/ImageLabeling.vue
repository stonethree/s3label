<template>
    <div id="image_labeling" class="container">
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
                    <button type="submit" onclick="clearCanvas();">Clear canvas</button>
                </div>
            </div>
        </div>

        <div id="canvasesdiv" style="position:relative; ">
            <canvas id="canvas-fg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;" v-draw-on-canvas="polygons"></canvas>
            <canvas id="canvas-bg" width="900" height="350" style="width:900px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
        </div>
    </div>
</template>

<script>
export default {
    name: 'image_labeling',
    data: function() {
        return {
            // TODO: store selected label task here, compute list of labels and disable/set drawing modes as specified in the label task
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            previous_tool: null,
            previous_mode: null,
            labels: [{"label_class": "Individual rock", "color": [255, 0, 0]}, 
                     {"label_class": "Belt", "color": [0, 255, 0]}, 
                     {"label_class": "Other", "color": [0, 0, 255]}],
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
        }
    },
    created: function () {
        // initialise active label to the first label in the set
        this.active_label = this.labels[0].label_class;
        console.log(this.labels[0].label_class)
    },
    watch: {
        active_tool: function (newActiveTool, oldActiveTool) {
            this.previous_tool = oldActiveTool;
        },
        active_mode: function (newActiveMode, oldActiveMode) {
            this.previous_mode = oldActiveMode;
        }
    },
    methods: {
        strokeThicknessChange: function(event) {
            console.log(event);
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
            console.log("length: ", binding.value.length, binding.value)
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