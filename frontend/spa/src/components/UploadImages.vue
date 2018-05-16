<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col small not-inlined">
                <div class="row image_list">
                    <h4>Datasets</h4>
                    <button type="submit" @click="get_datasets_list">Refresh list</button>
                    <b-table class="tables" responsive="md" hover :items="datasets" small @row-clicked="select_dataset">
                    </b-table>
                </div>

                <div class="row folder_selection">
                    <h4>Folder to upload from</h4>
                    <label for="folder_path"><b>Folder path</b></label>
                    <input type="text" placeholder="Enter folder path" name="folder_path" required v-model="folder_path">
                    <button type="submit" v-on:click="find_images('false')">Find images in folder</button>
                    <button type="submit" v-on:click="find_images('true')">Find images in folder recursively</button>
                </div>
                <div class="row image_list">
                    <h4>Files available for upload</h4>
                    <button type="submit" @click="select_all">Select All</button>
                    <button type="submit" @click="select_none">Select None</button>
                    <b-table class="tables" responsive="md" hover :items="image_paths" :fields="image_fields" small @row-clicked="select_image">
                        <template slot="is_selected" slot-scope="row">
                            <b-form-checkbox v-model="row.item.selected"></b-form-checkbox>
                        </template>
                    </b-table>
                    <button type="submit" @click="upload_images">Upload selected images</button>
                </div>
            </div>

            <div class="col">
                <div>
                    <div id="canvasesdiv" style="position:relative;" >
                        <canvas id="canvas-fg-2" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;"></canvas>
                        <canvas id="canvas-bg-2" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

var baseUrl = process.env.API_ADDR;
axios.defaults.baseURL = baseUrl;


export default {
    name: "upload_images",
    data: function() {
        return {
            folder_path: undefined,
            image_paths: undefined,
            input_data_path: undefined,
            padX: 20,
            padY: 20,
            dataset_fields: [{key: 'is_selected', label: 'Selected'},
                             'dataset_id',
                             'description'],
            image_fields: [{key: 'is_selected', label: 'Selected'},
                           'input_data_path'],
            datasets: [],
            dataset_id: undefined
        };
    },

    watch: {
        input_data_path: function () {
            if (this.input_data_path != undefined) {
                this.fetchAndDisplayImage(baseUrl + '/images_on_disk', this.input_data_path);
            }
        }
    },

    mounted: function() {
        this.get_datasets_list();
    },

    methods: {
        get_datasets_list: function() {
            // get list of datasets available to upload images to

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
                .get("/datasets", config)
                .then(function(response) {
                    console.log(response.data)
                    vm.datasets = response.data;
                })
                .catch(function(error) {
                    console.log(error);
                    vm.datasets = undefined;
                });
        },

        find_images: function(recursive) {
            // get list of images in folder

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
                .get("/image_paths?folder_path=" + this.folder_path + "&recursive=" + recursive, config)
                .then(function(response) {
                    console.log(response.data)
                    // var image_paths = response.data;
                    vm.image_paths = response.data.image_paths.map(function(im_path) { return {'input_data_path': im_path, 'selected': true} })
                })
                .catch(function(error) {
                    console.log(error);
                    vm.image_paths = undefined;
                });
        },

        upload_images: function() {
            if (this.dataset_id != undefined) {
                for (var i = 0; i < this.image_paths.length; i++) {
                    if (this.image_paths[i].selected) {
                        this.upload_image(this.image_paths[i].input_data_path, this.dataset_id);
                        console.log('uploaded:', this.image_paths[i].input_data_path, this.dataset_id)
                    }
                }
            }
        },

        upload_image: function(image_path, dataset_id) {
            // upload selected images to the database

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            let data = {
                "input_data_path": image_path,
                "dataset_id": dataset_id
            }

            axios
                .post("/input_data", data, config)
                .then(function(response) {
                    console.log("uploaded image successfully", response.data)
                })
                .catch(function(error) {
                    console.log("error uploading image", error);
                });
        },

        select_all: function() {
            for (var i = 0; i < this.image_paths.length; i++) {
                this.image_paths[i].selected = true;
            }
        },

        select_none: function() {
            for (var i = 0; i < this.image_paths.length; i++) {
                this.image_paths[i].selected = false;
            }
        },

        select_dataset: function(item, index, event) {
            this.dataset_id = item.dataset_id;

            // highlight selected row

            for (var i = 0; i < this.datasets.length; i++) {
                if (this.datasets[i].dataset_id == this.dataset_id) {
                    this.$set(this.datasets[i], '_rowVariant', 'active');
                }
                else {
                    this.$set(this.datasets[i], '_rowVariant', undefined);
                }
            }

            console.log('dataset_id:', this.dataset_id)
        },

        select_image: function(item, index, event) {
            this.input_data_path = item.input_data_path;

            // highlight selected row

            for (var i = 0; i < this.image_paths.length; i++) {
                if (this.image_paths[i].input_data_path == this.input_data_path) {
                    this.$set(this.image_paths[i], '_rowVariant', 'active');
                }
                else {
                    this.$set(this.image_paths[i], '_rowVariant', undefined);
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
            let canvas_fg = document.getElementById("canvas-fg-2");
            let canvas_bg = document.getElementById("canvas-bg-2");
            let ctx2 = canvas_bg.getContext("2d");    

            let img = new Image();
            let imgUrl = URL.createObjectURL(responseAsBlob);

            var vm = this;

            img.onload = function () {
                vm.setCanvasSize(canvas_fg, img.width, img.height, vm.padX, vm.padY);
                vm.setCanvasSize(canvas_bg, img.width, img.height, vm.padX, vm.padY);
                ctx2.drawImage(img, vm.padX, vm.padY);
                console.log('should display im', canvas_bg, img.width, img.height, vm.padX, vm.padY)
            }
            img.src = imgUrl;
        },

        fetchAndDisplayImage: function (pathToResource, input_data_path) {

            console.log('fetching im')
            
            // let access_token = localStorage.getItem("s3_access_token");

            var payload = {
                input_data_path: input_data_path
            };

            fetch(pathToResource, { 
                  headers: {'Accept': 'application/json',
                            'Content-Type': 'application/json'}, 
                  method: "POST", 
                  body: JSON.stringify(payload)
                })
                .then(this.validateResponse)
                .then(this.readResponseAsBlob)
                .then(this.showImage)
                .catch(function(error) {
                    console.log('error fetching and displaying image:', error);
                });
        },
    }
};
</script>

<style>
.folder_selection { padding-top: 2em }
.image_list { padding-top: 2em }
.not-inlined div { display: block }
.tables { cursor: pointer }
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>