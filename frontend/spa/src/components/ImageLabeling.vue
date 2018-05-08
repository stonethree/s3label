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
                <div class="col">
                    <div class="row modal-button">
                        <b-btn v-b-modal.hotkeyModal>Keyboard Shortcuts</b-btn>
                    </div>
                    <div class="row modal-button">
                        <b-btn v-if="label_examples != undefined" v-b-modal.exampleLabelingsModal>Labeling Examples</b-btn>
                        <b-btn v-else v-b-modal.exampleLabelingsModal disabled>Labeling Examples</b-btn>
                    </div>
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
                            v-bind:delete_event="delete_event"
                            v-bind:deselect_event="deselect_event"
                            v-bind:undo_event="undo_event"
                            v-bind:redo_event="redo_event"
                            v-bind:hide_polygons="hide_polygons"
                            ref="mySubComponent"
                            class="row"
                            ></drawing-canvas>
            </div>
            <!-- use a v-if to display error with slot if no images found: https://vuejs.org/v2/guide/components.html#Content-Distribution-with-Slots -->
        </div>

        <b-modal id="hotkeyModal" title="Keyboard Shortcuts" ok-only>
            <b-table striped hover :items="keyboard_shortcuts">
                <span slot="action" slot-scope="data" v-html="data.value">     
                </span>
            </b-table>
        </b-modal>

        <b-modal id="exampleLabelingsModal" title="Labeling Examples" ok-only size="lg">
            <div>
                <b-carousel id="examples-carousel" controls indicators img-width="800" img-height="600">
                    <b-carousel-slide v-for="example in label_examples" 
                                      :key="example.example_labeling_id"
                                      :caption="example.title" 
                                      :text="example.description" 
                                      :img-src="baseUrl + '/example_images/' + example.example_labeling_id"></b-carousel-slide>
                </b-carousel>
            </div>
        </b-modal>
    </div>
</template>

<script>

import DrawingCanvas from './DrawingCanvas'

import { uploadLabels,
         loadLabels,
         getLabelId } from '../../static/label_loading'

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
            clear_canvas_event: false,
            delete_event: false,
            clear_canvas_event: false,
            deselect_event: false,
            undo_event: false,
            redo_event: false,
            hide_polygons: false,
            label_examples: undefined,
            baseUrl: baseUrl,
            keyboard_shortcuts: [
                { key: 'Left', action: 'Go to previous image' },
                { key: 'Right', action: 'Go to next image or request new image to label' },
                { key: 'Space bar', action: 'Temporarily activate "select" mode' },
                { key: 'Shift', action: 'Temporarily activate "append" mode' },
                { key: 'Alt', action: 'Temporarily activate "erase" mode' },
                { key: 'Ctrl+Z', action: 'Undo <br><b>NB: does not currently undo canvas delete!</b>' },
                { key: 'Ctrl+Y', action: 'Redo' },
                { key: 'Escape', action: 'Deselect all regions' },
                { key: 'Delete', action: 'Delete selected region' },
                { key: 'H', action: 'Temporarily hide labels<br><em>Useful for checking the edge of the label against the underlying image</em>' },
            ]
        };
    },
    components: {
        DrawingCanvas,
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task',
            'labels',
            'label_task_id'
        ]),
        ...mapGetters('user_login', [
            'user_id'
        ]),
        ...mapGetters('image_labeling', [
            'input_data_id',
            'label_id'
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

        // display first image and its label, if available

        this.set_first_image();

        // get labeling examples to illustrate to user how to label for this task

        this.get_label_examples();
    },
    beforeDestroy () {
        window.removeEventListener('keydown', this.keyDownHandler);
        window.removeEventListener('keyup', this.keyUpHandler);
    },
    beforeRouteLeave (to, from, next) {
        // get current polygons array from drawing canvas component (NB: this isn't the most elegant solution, but it will do for now)
        var tmp = this.$refs.mySubComponent.fetch_polygons();
        var polygons = tmp.polygons;
        var edited = tmp.edited;

        if (edited) {
            console.log('save now!')

            var vm = this;

            uploadLabels(this.input_data_id, this.label_task_id, polygons)  // upload the labels from the previous image
            .then( function() {
                vm.$store.dispatch('image_labeling/leave_page');
            });
        }
        else {
            this.$store.dispatch('image_labeling/leave_page');
        }

        console.log('-----  leaving page')

        next()
    },

    methods: {
        set_first_image: async function () {
            var old_input_data_id = this.input_data_id;
            var vm = this;

            if (this.input_data_id_start != undefined) {
                // an initial image is specified, so load this image
                await this.$store.dispatch('image_labeling/set_initial_image', this.input_data_id_start);

                console.log('^^^^^^^^^^^ deciding if to load labels', vm.input_data_id, old_input_data_id)

                if (vm.input_data_id != old_input_data_id) {
                    // load the labels from the next image
                    let polygons_new = await loadLabels(vm.input_data_id, vm.label_task_id);

                    if (polygons_new != undefined) {
                        console.log('setting polygons:', polygons_new)
                        vm.$refs.mySubComponent.set_polygons(polygons_new);
                    }
                }
            }
            else {
                // no initial image specified. Request a new unlabeled image
                await this.$store.dispatch('image_labeling/next_image', this.label_task.label_task_id);

                if (vm.input_data_id != old_input_data_id) {
                    console.log('^^^^^^^^^^^loading labels2')
                    // load the labels from the next image
                    let polygons_new = await loadLabels(vm.input_data_id, vm.label_task_id);

                    if (polygons_new != undefined) {
                        console.log('^^^^^^^^^^^ setting polygons:', polygons_new)
                        vm.$refs.mySubComponent.set_polygons(polygons_new);
                    }
                }
            }
        },

        switch_image: async function (next_or_previous='next_image') {
            // switch to next or previous image

            if (next_or_previous != 'next_image' && next_or_previous != 'previous_image') {
                throw Error('Unexpected next_ore_previous parameter. Unable to switch image.');
                return -1;
            }

            var old_input_data_id = this.input_data_id;
            var old_label_id = this.label_id;

            // get current polygons array from drawing canvas component (NB: this isn't the most elegant solution, but it will do for now)
            var tmp = this.$refs.mySubComponent.fetch_polygons();
            var polygons = tmp.polygons;
            var edited = tmp.edited;

            var vm = this;

            if (edited) {
                await uploadLabels(this.input_data_id, this.label_task_id, polygons)  // upload the labels from the previous image
                .catch(function(error) {
                    console.log('error getting label ID:', error, vm.label_task_id, vm.input_data_id, vm.user_id);
                })
            }

            await vm.$store.dispatch('image_labeling/' + next_or_previous, vm.label_task.label_task_id)    // switch to the next image
            .then(function() {
                console.log('should load labels now...............', vm.input_data_id, old_input_data_id, vm.label_id, old_label_id)
                if (vm.input_data_id != old_input_data_id) {
                    console.log('loading image labels for:', vm.input_data_id, vm.label_task_id, vm.user_id)
                    
                    // load the labels from the next image
                    loadLabels(vm.input_data_id, vm.label_task_id)
                    .then(function(polygons_new) {
                        if (polygons_new != undefined) {
                            console.log('setting polygons:', polygons_new)
                            vm.$refs.mySubComponent.set_polygons(polygons_new);
                        }
                    });

                }
            });

        },

        get_label_examples: function() {
            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            var vm = this;

            axios
            .get("examples/label_tasks/" + this.label_task_id, config)
            .then(function(response) {
                vm.label_examples = response.data;
            })
            .catch(function(error) {
                console.log(error);
                vm.label_examples = undefined;
            });
        },

        keyDownHandler: function(e) {
            var key_handled = false;

            if (e.ctrlKey && e.code === "KeyZ") {
                console.log("Undo");
                this.undo_event = !this.undo_event;

                key_handled = true;
            }
            else if (e.ctrlKey && e.code === "KeyY") {
                console.log("Redo");
                this.redo_event = !this.redo_event;

                key_handled = true;
            }
            else if (e.code === "ArrowLeft") {

                this.switch_image('previous_image');
                
                key_handled = true;
            }
            else if (e.code === "ArrowRight") {

                this.switch_image('next_image');

                key_handled = true;
            }
            else if (e.code === 'Delete') {
                this.delete_event = !this.delete_event;

                key_handled = true;
            }
            else if (e.code === 'Escape') {
                this.deselect_event = !this.deselect_event;

                key_handled = true;
            }
            else if (e.code == 'Space') {
                if (this.previous_tool === undefined && !this.isDrawing) {
                    this.previous_tool = this.active_tool;
                    this.active_tool = 'select';
                }

                key_handled = true;
            }
            else if (e.code === 'KeyH') {
                this.hide_polygons = true;

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

            if (key_handled) {
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
            else if (e.code === 'KeyH') {
                this.hide_polygons = false;

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

            if (key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },

        clearCanvas: function() {
            this.clear_canvas_event = !this.clear_canvas_event;
            console.log('clear canvas called', this.clear_canvas_event)
        },

    },
}
</script>

<style>
#drawing-tools { border:black }
.modal-button { padding-top: 0.2em }
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