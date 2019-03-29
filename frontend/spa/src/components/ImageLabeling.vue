<template>
    <div id="image_labeling" class="container" >
        <div id="drawingtools" class="row">
            <div class="col">
                <div class="row justify-content-center">
                    <div id="tools" class="col border-right">
                        <div class="row">
                            <div class="col">Drawing Tool
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                <select width="100" style="width: 100px" id="tools_form" v-on:change="tool_selected" v-model="active_tool">
                                    <option v-for="(value,key) in tools_list" name="tool" :value="key">{{ value }}</option>
                                </select>
                            </div>
                        </div>
                        <div class="row" style="margin-bottom: 0.5rem">
                        </div>
                        <div class="row">
                            <div class="col">Zoom
                            </div>
                        </div>
                        <div class="row">
                            <div class="col" v-bind:key="zoom_state">
                                <i class="fa fa-search-minus" @click="keyDownHandler($event = {code: 'BracketLeft'})" style="cursor: pointer;"></i>
                                {{ zoom_state }}%
                                <i class="fa fa-search-plus" @click="keyDownHandler($event = {code: 'BracketRight'})" style="cursor: pointer;"></i>
                            </div>
                        </div>
                    </div>
                     
                    <div id="tool_modes" class="col border-right">
                        <div class="row">
                            <div class="col"> Freehand Mode
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                <select width="100" style="width: 100px"  id="mode_form" v-model="active_mode" v-bind:disabled="mode_disabled">
                                    <option class="radio-button" name="mode" value="new"> New </option>
                                    <option class="radio-button" name="mode" value="append"> Append </option>
                                    <option class="radio-button" name="mode" value="erase"> Erase </option>
                                </select>
                            </div>
                        </div>
                        <div class="row" style="margin-bottom: 0.5rem">
                        </div>
                        <div class="row">
                            <div class="col"> Allow Overlap
                            </div>
                        </div>
                        <div class="row justify-content-left" >
                            <div class="col">
                                <select width="100" style="width: 100px"  id="overlap_mode" v-model="active_overlap_mode" v-bind:disabled="overlap_mode_disabled" title="Choose whether labels can overlap each other or not.">
                                    <option class="radio-button" name="mode" value="overlap"> Yes </option>
                                    <option class="radio-button" name="mode" value="no-overlap"> No </option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col border-right">
                        <div class="row">
                            <div class="col">Label Class
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                <select v-model="active_label">                            
                                    <option v-for="label in labels" :key="label.label_class" name="semantic_label" :value="label.label_class">{{ label.label_class }}</option>
                                </select>
                            </div>
                        </div>
                        <div class="row" style="margin-bottom: .7rem;">
                        </div>
                        <div class="row">
                            <div class="col">
                                <button width="100" style="width: 100px; white-space: nowrap" type="submit" @click="clearCanvas">Clear canvas</button>
                            </div>
                        </div>
                    </div>
                    <div id="graphics_settings"  class="col border-right">
                        <div id="stroke_slider_container">
                            <span>Stroke thickness</span>
                            <input id="stroke_thickness_slider" type="range" min="0" max="10" class="slider" v-model="stroke_slider_value">
                        </div>
                        <div id="opacity_slider_container">
                            <span>Opacity</span>
                            <input id="opacity_slider" type="range" min="0" max="100" class="slider" v-model="opacity_slider_value">
                        </div>
                    </div>
                    <div id="image_settings"  class="col border-right">
                        <div id="brightness_slider_container">
                            <span>Brightness</span>
                            <input id="brightness_slider" type="range" min="-100" max="100" class="slider" v-model="brightness_slider_value">
                        </div>
                        <div id="contrast_slider_container">
                            <span>Contrast</span>
                            <input id="contrast_slider" type="range" min="-100" max="100" class="slider" v-model="contrast_slider_value">
                        </div>
                    </div>
                    <div class="col">
                        <div class="row">
                            <div class="col">
                                <div class="modal-button">
                                    <b-btn width="100" style="width:100px" v-b-modal.hotkeyModal>Hotkeys</b-btn>
                                </div>
                            </div>
                        </div>
                        <div class="row" style="margin-bottom: .5rem;">
                        </div>
                        <div class="row">
                            <div class="col">
                                <div class="modal-button">
                                    <b-btn width="100" style="width:100px" v-if="label_examples != undefined" v-b-modal.exampleLabelingsModal>Examples</b-btn>
                                    <b-btn width="100" style="width:100px" v-else v-b-modal.exampleLabelingsModal disabled>Examples</b-btn>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    
        <br>
        <div class="row" style="padding-top:30px; padding-bottom:10px">
            <div class="col">
                <div @click="switch_image('previous_image')" class="icon-style-left">
                    <span v-if="scroll.previous_cont" class="fa-stack">
                        <i class="fa fa-arrow-circle-left"></i>
                    </span>
                    <span v-else class="fa-stack">
                        <i class="fa fa-arrow-circle-left icon-dim"></i>
                    </span>
                </div>
            </div>
            <div class="col">
                <label-status v-bind:label-id="label_id" v-bind:user-completed-toggle="label_status_toggler.user_complete" class="label-status-style" style="width:370px;"></label-status>
            </div>
            <div class="col" v-if="label_task.enable_advanced_tools">   
                <span style="float:right">Filter</span>
            </div>
            <div class="col" v-if="label_task.enable_advanced_tools">
                <select v-on:change="filtered" v-model="image_filter">
                    <option value="filter_all">No image filter</option>
                    <option value="filter_complete">Images you have finished labeling</option>
                    <option value="filter_incomplete">Images you have not finished labeling</option>
                </select>
            </div>
            <div class="col">
                <div @click="switch_image('next_image')" class="icon-style-right">
                    <span v-if="scroll.next_cont" class="fa-stack">
                        <i class="fa fa-arrow-circle-right"></i>
                    </span>
                    <span v-else class="fa-stack">
                        <i class="fa fa-arrow-circle-right icon-dim"></i>
                    </span>
                </div>
            </div>
        </div>
        <div class="row justify-content-center">
            <drawing-canvas
                    v-bind:active_tool="active_tool"
                    v-bind:active_mode="active_mode"
                    v-bind:active_overlap_mode="active_overlap_mode"
                    v-bind:active_label="active_label"
                    v-bind:input_data_id="input_data_id"
                    v-bind:label_task_id="label_task.label_task_id"
                    v-bind:stroke_thickness="stroke_thickness"
                    v-bind:use_stroke="use_stroke"
                    v-bind:opacity="opacity"
                    v-bind:brightness="brightness"
                    v-bind:contrast="contrast"
                    v-bind:clear_canvas_event="clear_canvas_event"
                    v-bind:delete_event="delete_event"
                    v-bind:deselect_event="deselect_event"
                    v-bind:undo_event="undo_event"
                    v-bind:redo_event="redo_event"
                    v-bind:hide_labels="hide_labels"
                    v-bind:increase_circle_event="increase_circle_event"
                    v-bind:decrease_circle_event="decrease_circle_event"
                    v-bind:change_radio_event ="change_radio_event"
                    v-bind:switch_label_event="switch_label_event"
                    v-bind:zoom_level="zoom_level"
                    v-bind:image_filter="image_filter"
                    ref="mySubComponent"
                    >
            </drawing-canvas>
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
import LabelStatus from './LabelStatus'

import { uploadLabels,
         loadLabels,
         getLabelId } from '../../static/label_loading'

import { mapGetters } from 'vuex'
import axios from "axios";

var baseUrl = process.env.API_ADDR;
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
            brightness_slider_value: "0",
            contrast_slider_value: "0",
            clear_canvas_event: false,
            delete_event: false,
            clear_canvas_event: false,
            deselect_event: false,
            undo_event: false,
            redo_event: false,
            hide_labels: false,
            increase_circle_event: false,
            decrease_circle_event: false,
            switch_label_event: false,
            change_radio_event:false,
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
                { key: '1, 2, ...', action: 'Select label class' },
            ],
            tools_list: {},
            mode_disabled: false,
            overlap_mode_disabled: false,
            label_status_toggler: {user_complete: false},
            save_timer: '',
            zoom_state: 100,
            image_filter: "filter_all",
            scroll: {
                next_cont:true,
                previous_cont:false,
            },
        };
    },
    created: function() {
        this.save_timer = setInterval(this.save_progress, 5000);
    },
    components: {
        DrawingCanvas,
        LabelStatus
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task',
            'labels',
            'label_task_id',
            'default_tool',
            'allowed_tools',
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
        brightness: function() {
            return parseFloat(this.brightness_slider_value) / 100.;
        },
        contrast: function() {
            return parseFloat(this.contrast_slider_value) / 100.;
        },
        zoom_level: function() {
            return this.zoom_state;
        }
    },
    beforeMount() {
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);
    },
    mounted() {
        // initialise active label to the first label in the set
        console.log("Mounted")
        this.disableDrawTools();
        this.tool_selected();
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
        clearInterval(this.save_timer);
    },
    beforeRouteLeave (to, from, next) {
        // get current polygons array from drawing canvas component (NB: this isn't the most elegant solution, but it will do for now)
        var tmp = this.$refs.mySubComponent.fetch_labels();
        var labels = tmp.labels;
        var edited = tmp.edited;

        if (edited) {
            console.log('save now!')

            var vm = this;

            uploadLabels(this.input_data_id, this.label_task_id, labels)  // upload the labels from the previous image
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
        
        tool_selected: function() {
            console.log("tool_selected: "+this.active_tool)
            if (this.active_tool == "freehand"){
                this.mode_disabled = false;
                this.overlap_mode_disabled = false;
            }
            else {
                this.mode_disabled = true;
                this.overlap_mode_disabled = true;
                this.active_overlap_mode = "overlap"
            }
        },
        
        set_first_image: async function () {
            var old_input_data_id = this.input_data_id;
            var vm = this;

            if (this.input_data_id_start != undefined) {
                // an initial image is specified, so load this image
                
                await this.$store.dispatch('image_labeling/set_initial_image', this.input_data_id_start);

                console.log('^^^^^^^^^^^ deciding if to load labels', vm.input_data_id, old_input_data_id)

                if (vm.input_data_id != old_input_data_id) {
                    // load the labels from the next image
                    let labels_new = await loadLabels(vm.input_data_id, vm.label_task_id);

                    if (labels_new != undefined) {
                        console.log('setting labels:', labels_new)
                        vm.$refs.mySubComponent.set_labels(labels_new);
                    }
                }
            }
            else {
                // no initial image specified. Request a new unlabeled image
                
                var payload = {'task_id': this.label_task.label_task_id, 'label_filter': this.image_filter}
                await this.$store.dispatch('image_labeling/next_image', payload);
                
                vm.scroll.next_cont = true;
                vm.scroll.previous_cont = true;
                if (vm.image_filter != "filter_all") {
                    vm.scroll.previous_cont = false;
                }

                if (vm.input_data_id != old_input_data_id) {
                    console.log('^^^^^^^^^^^loading labels2')
                    // load the labels from the next image
                    let labels_new = await loadLabels(vm.input_data_id, vm.label_task_id);

                    if (labels_new != undefined) {
                        console.log('^^^^^^^^^^^ setting labels:', labels_new)
                        vm.$refs.mySubComponent.set_labels(labels_new);
                    }
                    else {
                        vm.scroll.next_cont = false;
                    }
                }
            }
        },

        switch_image: async function (next_or_previous='next_image') {
            // switch to next or previous image
            if (next_or_previous != 'next_image' && next_or_previous != 'previous_image') {
                console.error('Error: Unexpected next_ore_previous parameter. Unable to switch image.');
                return -1;
            }

            var old_input_data_id = this.input_data_id;
            var old_label_id = this.label_id;
            var vm = this;

            //upload the labels from the previous image
            this.save_progress();;
            
            var payload = {'task_id': this.label_task.label_task_id, 'label_filter': this.image_filter}
            await vm.$store.dispatch('image_labeling/' + next_or_previous, payload)    // switch to the next image
            .then(function() {
                console.log('should load labels now...............', vm.input_data_id, old_input_data_id, vm.label_id, old_label_id)
                
                //Update the previous_next scrolling icons
                vm.scroll.next_cont = true;
                vm.scroll.previous_cont = true;
                if (vm.input_data_id == undefined) {
                    vm.scroll.next_cont = false;
                }
                else if (vm.input_data_id == old_input_data_id) {
                    vm.scroll.previous_cont = false;
                }
                
                if (vm.input_data_id != old_input_data_id) {
                    console.log('loading image labels for:', vm.input_data_id, vm.label_task_id, vm.user_id)
                    
                    // load the labels from the next image
                    loadLabels(vm.input_data_id, vm.label_task_id)
                    .then(function(lab_new) {
                        if (lab_new != undefined) {
                            console.log('setting labels:', lab_new);
                            vm.$refs.mySubComponent.set_labels(lab_new);
                        }
                    });
                }
            });
        },

        save_progress: async function() {
            // get current labels array from drawing canvas component (NB: this isn't the most elegant solution, but it will do for now)
            var tmp = this.$refs.mySubComponent.fetch_labels();
            console.log(tmp);
            var lab = tmp.labels;
            var edited = tmp.edited;
            var vm = this;
            
            if (edited) {
                await uploadLabels(this.input_data_id, this.label_task_id, lab) 
                .catch(function(error) {
                    console.log('error getting label ID:', error, vm.label_task_id, vm.input_data_id, vm.user_id);
                })
                
                console.log('current progress saved')
            }
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
                this.hide_labels = true;

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
            else if(e.code === 'NumpadAdd') {
                this.increase_circle_event = !this.increase_circle_event;
                key_handled = true;
            }
            else if(e.code === 'NumpadSubtract') {
                this.decrease_circle_event = !this.decrease_circle_event;
                key_handled = true;
            }
            else if (e.code == 'BracketLeft') {
                var inc = -10;
                this.zoom_state += inc;
                if (this.zoom_state <= 10) {
                    this.zoom_state = 10
                }
            }
            else if (e.code == 'BracketRight') {
                var inc = 10;
                this.zoom_state += inc;
            }
            if ((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105)) {
                // 0-9 only
                this.switch_label_event = !this.switch_label_event;
                let label_index = e.keyCode - 48;

                if (label_index >= 1 && label_index <= this.labels.length) {
                    try {
                        this.active_label = this.labels[label_index - 1].label_class;
                    }
                    catch (err) {
                        console.log('Error switching active label:', err);
                    }
                }
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
                this.hide_labels = false;

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

            if (key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },

        clearCanvas: function() {
            this.clear_canvas_event = !this.clear_canvas_event;
            console.log('clear canvas called', this.clear_canvas_event)
        },
        
        changeRadio: function(){
            this.change_radio_event = !this.change_radio_event;
        },

        filtered: function(){
            this.save_progress();
            this.$store.dispatch('image_labeling/change_filter');
            this.set_first_image()
        },
        
        defaultDrawTools: function() {
            this.tools_list = {};
            this.tools_list["freehand"] = "Freehand";
            this.tools_list["polygon"] = "Polygon";
            this.tools_list["rectangle"] = "Rectangle";
            this.tools_list["point"] = "Point";
            this.tools_list["circle"] = "Circle";
            this.tools_list["select"] = "Select";
        },
        
        disableDrawTools: function() {
            console.log("disableDrawTools")
            var enabled_tools = [];
            if (this.allowed_tools != null && this.allowed_tools != 'none') {
                enabled_tools = this.allowed_tools.split(", ");
            }
            this.active_tool = this.default_tool;
            enabled_tools.push(this.default_tool);
            console.log(enabled_tools)
            this.tools_list = {};
            for (let i = 0; i < enabled_tools.length; i++) {
                switch(enabled_tools[i]) {
                    case 'freehand':
                        this.tools_list["freehand"]="Freehand"
                        break;
                    case 'polygon':
                        this.tools_list["polygon"]="Polygon"
                        break;
                    case 'rectangle':
                        this.tools_list["rectangle"]="Rectangle"
                        break;
                    case 'point':
                        this.tools_list["point"]="Point"
                        break;
                    case 'circle':
                        this.tools_list["circle"]="Circle"
                        break;
                    case 'null':
                        defaultDrawTools();
                        break;
                }
            }
            this.tools_list["select"]="Select";
        },
        
    },
}
</script>

<style>
.modal-button { padding-top: 0.2em }
.icon-style-left {
    float: right;
    cursor: pointer;
}
.icon-style-right {
    float: left;
    cursor: pointer;
}

</style>