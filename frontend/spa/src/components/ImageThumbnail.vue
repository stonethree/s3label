<template>
    <div>
        <div v-bind:id="userLabeledData.input_data_id" class="canvasesdiv" @click="openImage">
            <canvas v-bind:id="canvas_bg_id" width="300" height="300" style="width:300px;height:300px; border: 1px solid #ccc; z-index: 2; "></canvas>
        </div>
    </div>
</template>

<script>
import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

export default {
    name: "image_thumbnail",
    props: ['userLabeledData'],
    data: function() {
        return {
            padX: 10,
            padY: 10
        };
    },
    computed: {
        canvas_bg_id: function() {
            return 'canvas-bg-' + this.userLabeledData.input_data_id;
        },
        canvas_fg_id: function() {
            return 'canvas-fg-' + this.userLabeledData.input_data_id;
        },
        image_request_path: function () {
            return baseUrl + "/input_images/" + this.userLabeledData.input_data_id;
        }
    },
    beforeMount() {
        this.fetchAndDisplayImage(this.image_request_path);
    },
    methods: {
        openImage: function () {
            console.log('open image for labeling', this.userLabeledData.input_data_id)
            this.$router.push({name: 'image_labeler', params: {input_data_id_start: this.userLabeledData.input_data_id}});
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
            let canvas_bg = document.getElementById(this.canvas_bg_id);

            let ctx2 = canvas_bg.getContext("2d");    

            let img = new Image();
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                var f = 4;
                vm.setCanvasSize(canvas_bg, img.width/f, img.height/f, vm.padX, vm.padY);
                ctx2.drawImage(img, vm.padX, vm.padY, img.width/f, img.height/f);
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
                    console.log(error);
                });
        },
    }
};
</script>

<style>
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