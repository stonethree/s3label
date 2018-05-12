<template>
    <div class="image-with-label">
        <label-status class="labelstatus" v-bind:label-id="label_id"></label-status>
        <div v-bind:id="userLabeledData.input_data_id" class="canvasesdiv" @click="openImage">
            <canvas v-bind:id="canvas_bg_id" width="300" height="300" style="width:300px;height:300px; border: 1px solid #ccc; z-index: 2; " 
                    data-toggle="tooltip" v-bind:title="tooltip_text"></canvas>
        </div>
    </div>
</template>

<script>

import { mapGetters } from 'vuex'

import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

import LabelStatus from './LabelStatus'

import { getLabelId } from '../../static/label_loading'

function chooseImageDimensions(w, h, max_h) {
    // calculate image width and height such that height is at most max_w and max_h, while preserving aspect ratio

    return {'new_h': max_h,
            'new_w': max_h / h * w};
}

export default {
    name: "image_thumbnail",
    props: ['userLabeledData'],
    data: function() {
        return {
            padX: 10,
            padY: 10,
            im_height_max: 150,
            label_id: undefined
        };
    },
    components: {
        LabelStatus,
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task_id'
        ]),
        ...mapGetters('user_login', [
            'user_id'
        ]),
        canvas_bg_id: function() {
            return 'canvas-bg-' + this.userLabeledData.input_data_id;
        },
        canvas_fg_id: function() {
            return 'canvas-fg-' + this.userLabeledData.input_data_id;
        },
        image_request_path: function () {
            return baseUrl + "/input_images/" + this.userLabeledData.input_data_id + "?height=" + this.im_height_max;
        },
        tooltip_text: function() {
            return 'Label ID: ' + this.label_id;
        }
    },
    beforeMount() {
        this.fetchAndDisplayImage(this.image_request_path);
        this.get_label_id();
    },
    methods: {
        openImage: function () {
            console.log('open image for labeling', this.userLabeledData.input_data_id)
            this.$router.push({name: 'image_labeler', params: {input_data_id_start: this.userLabeledData.input_data_id}});
        },

        get_label_id: function () {
            var vm = this;

            getLabelId(this.label_task_id, this.userLabeledData.input_data_id, this.user_id)
                .then(function(label_id) {
                        vm.label_id = label_id;
                    })
                    .catch(function(error) {
                        console.error('Error getting label ID:', error, vm.label_task_id, this.userLabeledData.input_data_id, vm.user_id);
                    });
        },

        // image displaying functions

        set_placeholder_image: function () {
            let canvas_bg = document.getElementById(this.canvas_bg_id);
            this.setCanvasSize(canvas_bg, this.im_height_max * 1.4, this.im_height_max, this.padX, this.padY);
        },

        validateResponse: function (response) {
            if (!response.ok) {
                throw Error('Error displaying image:', response.statusText);
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
            let canvas_bg = document.getElementById(this.canvas_bg_id);

            let ctx2 = canvas_bg.getContext("2d");    

            let img = new Image();
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                var new_dims = chooseImageDimensions(img.width, img.height, vm.im_height_max);

                vm.setCanvasSize(canvas_bg, new_dims['new_w'], new_dims['new_h'], vm.padX, vm.padY);
                ctx2.drawImage(img, vm.padX, vm.padY, new_dims['new_w'], new_dims['new_h']);
            }
            img.src = imgUrl;
        },

        fetchAndDisplayImage: function (pathToResource) {

            console.log('fetching im')
            
            // let access_token = localStorage.getItem("s3_access_token");
            var vm = this;

            fetch(pathToResource)
                .then(this.validateResponse)
                .then(this.readResponseAsBlob)
                .then(this.showImage)
                .catch(function(error) {
                    console.log(error, 'setting placeholder image');
                    vm.set_placeholder_image();
                });
        },
    }
};
</script>

<style>
.labelstatus { display: inline; }
.image-with-label { display: inline-block;
                    /* max-width: 400px; */
                     }
.canvasesdiv { display: inline;
               cursor: pointer }
/* .canvasesdiv canvas { display: inline } */
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>