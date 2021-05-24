<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col small not-inlined">
                <b-btn v-b-toggle.collapse1 variant="primary">Toggle Collapse</b-btn>
                <b-collapse id="collapse1" class="mt-2" visible>
                    <div class="row">
                        <h3>Users</h3>
                        <b-table class="tables" responsive="md" hover :items="users" :fields="fields_users" small @row-clicked="select_user"></b-table>
                    </div>
                    <div class="row">
                        <h3>Label tasks for user</h3>
                        <b-table class="tables" responsive="md" hover :items="label_tasks" :fields="fields_label_tasks" small @row-clicked="select_label_task"></b-table>
                    </div>
                </b-collapse>
                <div class="row">
                    <h3>Labeled data</h3>
                    <b-table class="tables" 
                        responsive="md" 
                        hover 
                        :items="labeled_input_data" 
                        :fields="fields_labeled_input_data" 
                        small @row-clicked="select_label" 
                        v-model="labels_table_data" 
                        :current-page="currentPageLabel" 
                        :per-page="perPageLabel"></b-table>
                </div>
                <b-col md="6" class="my-1">
                    <b-pagination :total-rows="totalRowsLabel" :per-page="perPageLabel" v-model="currentPageLabel" class="my-0" />
                </b-col>
            </div>

            <div class="col">
                <div>
                    <label-status v-if="input_data_id !=undefined" v-bind:label-id="label_id" mode="admin_mode"></label-status>
                    <div id="canvasesdiv" style="position:relative;" >
                        <canvas id="canvas-fg" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;"></canvas>
                        <canvas id="canvas-bg" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
// import moment from 'moment';
var moment = require('moment');
import axios from "axios";

var baseUrl = process.env.API_ADDR;
axios.defaults.baseURL = baseUrl;

function convertPolygonToPaths(polygon) {
    return polygon.regions;
}

import { addPaddingOffset } from '../../static/LabelOperations'
import { drawAllLabels } from '../../static/DrawingOperations'
import { extractColor, formatColor } from '../../static/color_utilities'
import LabelStatus from './LabelStatus.vue'


export default {
    name: "check_user_labeling",
    data: function() {
        return {
            user_id: undefined,
            label_task_id: undefined,
            users: undefined,
            label_tasks: undefined,
            labeled_input_data: undefined,
            input_data_id: undefined,
            label_id: undefined,
            padX: 80,
            padY: 80,
            lineWidth: 2,
            opacity: 0.3,
            stroke_thickness: 2,
            use_stroke: true,
            labels_table_data: undefined,
            hide_labels: false,
            perPageLabel: 10,
            currentPageLabel: 1,
            labelArr: []
        };
    },

    components: {
        LabelStatus,
    },

    beforeMount() {
        this.get_users();
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);
    },
    beforeDestroy () {
        window.removeEventListener('keydown', this.keyDownHandler);
        window.removeEventListener('keyup', this.keyUpHandler);
    },

    computed: {
        ctx: function() {
            let canvas_fg = document.getElementById("canvas-fg");
            return canvas_fg.getContext("2d");
        },
        label_task: function() {
            if (this.label_task_id != undefined) {
                return this.label_tasks.find(label_task => label_task.label_task_id === this.label_task_id)
            }
            else {
                return undefined;
            }
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
                    d[this.labels[i].label_class] = extractColor(this.labels[i].color);
                }
                return d;
            }
            else {
                return null
            }
        },
        fields_users: function() {
            return this.create_sortable_column_fields(this.users)
        },
        fields_label_tasks: function() {
            return this.create_sortable_column_fields(this.label_tasks)
        },
        fields_labeled_input_data: function() {
            return this.create_sortable_column_fields(this.labeled_input_data)
        },
        totalRowsLabel: function() {
            if (this.labeled_input_data != undefined) {
                return this.labeled_input_data.length;
            }
            else {
                return 0;
            }
        },
    },

    watch: {
        user_id: function () {
            this.get_label_tasks_for_user(this.user_id);
            this.get_labeled_input_data(this.label_task_id, this.user_id);
            // this.format_datestamps();
        },

        label_task_id: function () {
            this.get_labeled_input_data(this.label_task_id, this.user_id);
        },

        input_data_id: function () {
            if (this.input_data_id != undefined) {
                this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
                this.loadImageLabels(this.input_data_id);
            }
        }
    },

    methods: {
        create_sortable_column_fields: function(arr) {
            if (arr != undefined && arr.length >= 1) {
                let keys = Object.keys(arr[0]);
                keys = keys.filter(key => !key.startsWith('_'));
                return keys.map(key => {return {'key': key, 'sortable': true}});
            }
            else {
                return undefined;
            }
        },
        get_users: function() {
            // get list of users

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
                .get("/users", config)
                .then(function(response) {
                    console.log(response.data)

                    vm.users = response.data;
                })
                .catch(function(error) {
                    console.log(error);
                    vm.users = undefined;
                });
        },

        get_label_tasks_for_user: function (user_id) {
            // get list of label tasks for this user

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
                .get("/label_tasks/users/" + user_id, config)
                .then(function(response) {
                    console.log('vm.label_tasks:', response.data)

                    vm.label_tasks = response.data;
                })
                .catch(function(error) {
                    console.log(error);
                    vm.label_tasks = undefined;
                });
        },

        get_labeled_input_data: function (label_task_id, user_id) {
            if (label_task_id == undefined) {
                this.labeled_input_data = undefined;
            }
            else {
                // get list of label tasks for this user

                const vm = this;

                let access_token = localStorage.getItem("s3_access_token");

                let config = {
                    headers: {
                    Authorization: "Bearer " + access_token
                    }
                };

                axios
                    .get("/all_data/label_tasks/" + label_task_id + "/users/" + user_id, config)
                    .then(function(response) {
                        console.log(response.data)

                        vm.labeled_input_data = response.data;
                        vm.format_datestamps();
                    })
                    .catch(function(error) {
                        console.log(error);
                        vm.labeled_input_data = undefined;
                    });
            }
        },

        format_datestamps: function () {
            // convert from Unix timestamps to a comprehensible format for displaying in table
            console.log('labeled_input_data:', this.labeled_input_data)

            if (this.labeled_input_data != undefined) {
                for (let i = 0; i < this.labeled_input_data.length; i++) {
                    let timestamp = this.labeled_input_data[i].timestamp_edit / 1000;
                    this.labeled_input_data[i].timestamp_edit = moment.unix(timestamp).format("MMM DD YYYY, HH:mm:ss");
                }
                console.log('finished converting dates', this.labeled_input_data[0].timestamp_edit)
            }
        },

        select_user: function(item, index, event) {
            this.user_id = item.user_id;

            // highlight selected row

            for (var i = 0; i < this.users.length; i++) {
                if (this.users[i].user_id == this.user_id) {
                    this.$set(this.users[i], '_rowVariant', 'active');
                }
                else {
                    this.$set(this.users[i], '_rowVariant', undefined);
                }
            }

            // reset input data ID so that old image is no longer displayed

            this.label_task_id = undefined;
            this.input_data_id = undefined;
        },

        select_label_task: function(item, index, event) {
            this.label_task_id = item.label_task_id;

            // highlight selected row

            for (var i = 0; i < this.label_tasks.length; i++) {
                if (this.label_tasks[i].label_task_id == this.label_task_id) {
                    this.$set(this.label_tasks[i], '_rowVariant', 'active');
                }
                else {
                    this.$set(this.label_tasks[i], '_rowVariant', undefined);
                }
            }

            // reset input data ID so that old image is no longer displayed

            this.input_data_id = undefined;
        },

        select_label: function(item, index, event) {
            this.input_data_id = item.input_data_id;
            this.label_id = item.label_id;

            // highlight selected row
            this.labelArr = [];
            for (var i = 0; i < this.labeled_input_data.length; i++) {
                if (this.labeled_input_data[i].input_data_id == this.input_data_id) {
                    this.$set(this.labeled_input_data[i], '_rowVariant', 'active');
                }
                else {
                    this.$set(this.labeled_input_data[i], '_rowVariant', undefined);
                }
            }
        },

        // image displaying functions

        validateResponse: function (response) {
            if (!response.ok) {
                console.error(response.statusText);
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

                // redraw the labels, since we have just resized the canvas and so lost any currently displayed labels
                drawAllLabels(vm, vm.labelArr);
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

        loadImageLabels: function (input_data_id) {

            console.log('getting image labels with label task ID', this.label_task_id, 'and input data ID', input_data_id)

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            var vm = this;

            axios
                .get("labels/input_data/" + input_data_id + "/label_tasks/" + this.label_task_id + "/users/" + this.user_id, config)
                .then(function(response) {
                    if (response.data.length == 1) {
                        console.log("Label found for this image: attempting to apply it in the view")
                        let responseLabel = response.data[0];
                        console.log(response);
                        // check label format is correct

                        var labl = JSON.parse(responseLabel.label_serialised);
                        //console.log(labl);

                        if (labl.length > 0 && labl[0].label != undefined) {
                            console.log('Applied serialised label to image')
                            vm.labelArr = labl;

                            vm.labelArr = addPaddingOffset(vm.labelArr, vm.padX, vm.padY);
                            console.log(vm.labelArr);

                            drawAllLabels(vm, vm.labelArr);
                        }
                        else {
                            console.warn('Serialised label has wrong format or is empty:' + labl)
                        }
                    }
                    else if (response.data.length == 0) {
                        console.error("No label found for this image")
                    }
                    else {
                        console.error("Error: expected at most one label for this image!")
                    }
                })
                .catch(function(error) {
                    console.log(error);
                    vm.labelArr = [];
                    drawAllLabels(vm, vm.labelArr);
                });
        },

        keyDownHandler: function(e) {
            var key_handled = false;

            if (e.code === "ArrowUp") {

                // get index if currently highlighted row in the labels table
                let k = this.labels_table_data.findIndex(k => k._rowVariant=='active');

                if (k > 0) {
                    // set label ID to the above row's label ID
                    this.label_id = this.labels_table_data[k-1].label_id;
                    this.input_data_id = this.labels_table_data[k-1].input_data_id;

                    // highlight that row and unhighlight the current row
                    this.$set(this.labels_table_data[k], '_rowVariant', undefined);
                    this.$set(this.labels_table_data[k-1], '_rowVariant', 'active');
                }
                
                key_handled = true;
            }
            else if (e.code === "ArrowDown") {

                // get index if currently highlighted row in the labels table
                let k = this.labels_table_data.findIndex(k => k._rowVariant=='active');

                if (k >= 0 && k < this.labels_table_data.length - 1) {
                    // set label ID to the above row's label ID
                    this.label_id = this.labels_table_data[k+1].label_id;
                    this.input_data_id = this.labels_table_data[k+1].input_data_id;

                    // highlight that row and unhighlight the current row
                    this.$set(this.labels_table_data[k], '_rowVariant', undefined);
                    this.$set(this.labels_table_data[k+1], '_rowVariant', 'active');
                }

                key_handled = true;
            }
            else if (e.code === 'KeyH') {
                this.hide_labels = true;
                drawAllLabels(this, this.labelArr);

                key_handled = true;
            }

            if (key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },

        keyUpHandler: function(e) {
            var key_handled = false;

            if (e.code === 'KeyH') {
                this.hide_labels = false;
                drawAllLabels(this, this.labelArr);

                key_handled = true;

                console.log('H up')
            }

            if (key_handled) {
                e.stopPropagation();
                e.preventDefault();
            }
        },
    }
};
</script>

<style>
.not-inlined div { display: block }
.tables { cursor: pointer }
</style>
