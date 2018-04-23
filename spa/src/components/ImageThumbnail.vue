<template>
    <div>
        <!-- <div class="card" style="background-color:hsla(20, 100%, 64%, 0.7);">
            <div class="card-body">
                <h4 class="card-title"> {{ lt.label_task_id }} - {{ lt.title }} </h4>
                <h6 class="card-subtitle mb-2 font-italic"> {{ lt.type }} </h6>
                <p> {{ lt.description }} </p>
                <button v-on:click="select_label_task(lt.label_task_id)"> Label data </button>
                <button v-on:click="view_labeled_data(lt.label_task_id)"> View labeled data </button>
            </div>
        </div> -->



        <div v-bind:id="userLabeledData.input_data_id" class="canvasesdiv" @click="openImage"> <!--style="position:relative;"> -->
            <canvas v-bind:id="canvas_bg_id" width="300" height="300" style="width:300px;height:300px; border: 1px solid #ccc; z-index: 2; "></canvas>
            <!-- <canvas v-bind:id="canvas_fg_id" width="300" height="300" style="width:300px;height:300px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas> -->
        </div>
    </div>
</template>

<script>
import axios from "axios";

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
    name: "image_thumbnail",
    props: ['userLabeledData'],
    data: function() {
        return {
            image_title: "image title...",
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
            return "http://127.0.0.1:5000/image_labeler/api/v1.0/input_images/" + this.userLabeledData.input_data_id;
        }
    },
    beforeMount() {
        this.fetchAndDisplayImage(this.image_request_path);
        console.log('displaying im:::::', this.userLabeledData.input_data_id)
    },
    methods: {
        openImage: function () {
            console.log('open image for labeling', this.userLabeledData.input_data_id)
            this.$router.push('image_labeler');
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
            // let canvas_fg = document.getElementById(this.canvas_fg_id);
            let canvas_bg = document.getElementById(this.canvas_bg_id);

            let ctx2 = canvas_bg.getContext("2d");    

            let img = new Image();
            console.log(responseAsBlob)
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                // vm.setCanvasSize(canvas_fg, img.width, img.height, vm.padX, vm.padY);
                // vm.setCanvasSize(canvas_bg, img.width, img.height, vm.padX, vm.padY);
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
                .catch(this.logError);
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