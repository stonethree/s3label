<template>
    <div id="image_labeling" class="container" >
        <div id="drawingtools" class="row">
            <div class="col">
            <div class="row justify-content-center">
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
        </div>
    
        <div class="row justify-content-center">
            <div class="col">
            <drawing-canvas v-bind:active_tool="active_tool"
                            v-bind:active_mode="active_mode"
                            v-bind:active_overlap_mode="active_overlap_mode"
                            v-bind:active_label="active_label"
                            v-bind:input_data_id="input_data_id"
                            v-bind:label_task_id="label_task.label_task_id"
                            v-bind:stroke_thickness="stroke_thickness"
                            v-bind:use_stroke="use_stroke"
                            v-bind:opacity="opacity"
                            v-bind:clear_canvas_event="clear_canvas_event"
                            ref="mySubComponent"
                            class="row"
                            ></drawing-canvas>
            </div>
        </div>
    </div>
</template>

<script>

import DrawingCanvas from './DrawingCanvas'

import { mapGetters } from 'vuex'
import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;


export default {
    name: 'image_labeling',
    props: ['input_data_id_start'],
    data: function() {
        return {
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            previous_tool: undefined,
            previous_mode: undefined,
            active_label: undefined,
            stroke_slider_value: "2",
            opacity_slider_value: "50",
            clear_canvas_event: false
        };
    },
    components: {
        DrawingCanvas,
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task',
            'labels'
        ]),
        ...mapGetters('user_login', [
            'user_id'
        ]),
        ...mapGetters('image_labeling', [
            'input_data_id'
        ]),
        stroke_thickness: function() {
            return Math.max(1, parseInt(this.stroke_slider_value));
        },
        use_stroke: function() {
            return parseInt(this.stroke_slider_value) > 0 ? true : false; 
        },
        opacity: function() {
            return parseFloat(this.opacity_slider_value) / 100.;
        },

    },
    beforeMount() {
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);
    },
    mounted() {
        // initialise active label to the first label in the set

        if (this.labels != undefined && this.labels.length > 0) {
            this.active_label = this.labels[0].label_class;
        }

        // commit starting input data ID, whether defined or not

        this.$store.dispatch('image_labeling/set_input_data_id_of_existing_image', this.input_data_id_start);

        // if an image ID is specified, load that image

        if (this.input_data_id == undefined) {
            this.$store.dispatch('image_labeling/get_input_data_id_of_next_image', this.label_task.label_task_id);
        }
    },
    beforeDestroy () {
        window.removeEventListener('keydown', this.keyDownHandler);
        window.removeEventListener('keyup', this.keyUpHandler);

        // this.$store.dispatch('image_labeling/upload_labels_for_current_image', this.label_task.label_task_id)
    },
    beforeRouteLeave (to, from, next) {
        // notify drawing canvas to save image labels before navigating away

        // this.save_labels_toggler = !this.save_labels_toggler;

        console.log('save now!')

        this.$refs.mySubComponent.save_labels();

        this.$store.dispatch('image_labeling/clear_input_data_id');

        console.log('-----  leaving page')

        next()
    },

    methods: {

        keyDownHandler: function(e) {
            var key_handled = false;

            if (e.ctrlKey && e.code === "KeyZ") {
                console.log("Undo");
                this.undo();
                // this.drawAllPolygons(this.ctx, this.polygons);

                key_handled = true;
            }
            else if (e.ctrlKey && e.code === "KeyY") {
                console.log("Redo");
                this.redo();
                // this.drawAllPolygons(this.ctx, this.polygons);

                key_handled = true;
            }
            else if (e.ctrlKey && e.code === "Enter") {
                // this.label_status_toggler.user_complete = !this.label_status_toggler.user_complete;

                key_handled = true;
            }
            else if (e.code === "ArrowLeft") {
                if (this.input_data_id == undefined) {
                    this.$store.dispatch('image_labeling/get_input_data_id_of_most_recently_labeled_image', this.label_task.label_task_id);
                }
                else {
                    this.$store.dispatch('image_labeling/get_input_data_id_of_previous_labeled_image', this.label_task.label_task_id);
                }
                
                key_handled = true;
            }
            else if (e.code === "ArrowRight") {
                this.$store.dispatch('image_labeling/get_input_data_id_of_next_image', this.label_task.label_task_id);

                key_handled = true;
            }
            else if (e.code === 'Delete') {
                // console.log('num orig polys:', this.polygons.length, 'num redo polys:', this.polygons_redo.length)
                // this.polygons_undo.push(...this.polygons.filter(poly => poly.selected));
                // this.polygons = this.polygons.filter(poly => !poly.selected);
                // console.log('num final polys:', this.polygons.length, 'num redo polys:', this.polygons_redo.length)
                // // this.drawAllPolygons(this.ctx, this.polygons);

                key_handled = true;
            }
            else if (e.code === 'Escape') {
                // for (let i = 0; i < this.polygons.length; i++) {
                //     this.polygons[i].selected = false;
                // }
                // // this.drawAllPolygons(this.ctx, this.polygons);

                key_handled = true;
            }
            else if (e.code == 'Space') {
                if (this.previous_tool === undefined && !this.isDrawing) {
                    this.previous_tool = this.active_tool;
                    this.active_tool = 'select';
                }

                key_handled = true;
            }
            else if (e.code.startsWith('Shift')) {
                if (this.previous_mode === undefined && !this.isDrawing) {
                    this.previous_mode = this.active_mode;
                    this.active_mode = 'append';
                }

                key_handled = true;
            }
            else if (e.code.startsWith('Alt')) {
                if (this.previous_mode === undefined && !this.isDrawing) {
                    this.previous_mode = this.active_mode;
                    this.active_mode = 'erase';
                }

                key_handled = true;
            }
            else {
                // console.log('key not found (down):', e.code);
            }

            if (!key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },

        keyUpHandler: function (e) {
            var key_handled = false;

            if (e.code === 'Space') {
                if (this.previous_tool) {
                    this.active_tool = this.previous_tool;
                    this.previous_tool = undefined;
                }

                key_handled = true;
            }
            else if (e.code.startsWith('Shift')) {
                if (this.previous_mode) {
                    this.active_mode = this.previous_mode;
                    this.previous_mode = undefined;
                }

                key_handled = true;
            }
            else if (e.code.startsWith('Alt')) {
                if (this.previous_mode) {
                    this.active_mode = this.previous_mode;
                    this.previous_mode = undefined;
                }

                key_handled = true;
            }
            else {
                // console.log('key not found (up):', e.code);
            }

            if (!key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },

        undo: function() {
            // if (this.polygons_undo.length > 0) {
            //     this.polygons.push(this.polygons_undo.pop());
            // }
            // else if (this.polygons.length > 0) {
            //     this.polygons_redo.push(this.polygons.pop());
            // }
        },

        redo: function() {
            // if (this.polygons_redo.length > 0) {
            //     this.polygons.push(this.polygons_redo.pop());
            // }
        },

        clearCanvas: function() {
            this.clear_canvas_event = !this.clear_canvas_event;
            console.log('clear canvas called', this.clear_canvas_event)
        },

    },
}
</script>

<style>
/* .canvas-section div { padding-top: 2em } */
/* #image_labeling {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>