<template>
    <div class="container">
        <div class="row">
            <div class="col">
                <div class="row">
                    <h3>Users</h3>
                    <b-table striped hover :items="users" small @row-clicked="select_user"></b-table>
                </div>
                <div class="row">
                    <h3>Label tasks for user</h3>
                    <b-table striped hover :items="label_tasks" small @row-clicked="select_label_task"></b-table>
                </div>
                <div class="row">
                    <h3>Labeled data</h3>
                    <b-table striped hover :items="labels" small @row-clicked="select_label"></b-table>
                </div>
            </div>

            <div class="col">
                <div>
                    <div id="canvasesdiv" style="position:relative;" > <!--@mousedown="mouseDownHandler" @mouseup="mouseUpHandler" @mousemove="mouseMoveHandler"> -->
                        <canvas id="canvas-fg" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 2; position:absolute; left:0px; top:0px;"></canvas>
                        <canvas id="canvas-bg" width="400" height="350" style="width:400px;height:350px; border: 1px solid #ccc; z-index: 1; position:absolute; left:0px; top:0px;"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

export default {
    name: "admin_view",
    data: function() {
        return {
            user_id: undefined,
            label_task_id: undefined,
            label_id: undefined,
            users: undefined,
            label_tasks: undefined,
            labels: undefined,
            input_data_id: undefined,
            padX: 20,
            padY: 20
        };
    },
    beforeMount() {
        this.get_users();
    },
    methods: {
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
                });
        },

        get_label_tasks: function (user_id) {
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
                    console.log(response.data)

                    vm.label_tasks = response.data;
                })
                .catch(function(error) {
                    console.log(error);
                });
        },

        get_labels: function (label_task_id, user_id) {
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

                    vm.labels = response.data;
                })
                .catch(function(error) {
                    console.log(error);
                });
        },

        select_user: function(item, index, event) {
            console.log(item, index, event)
            this.user_id = item.user_id;
        },

        select_label_task: function(item, index, event) {
            console.log(item, index, event)
            this.label_task_id = item.label_task_id;
        },

        select_label: function(item, index, event) {
            console.log(item, index, event)
            this.input_data_id = item.input_data_id;
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
    },

    watch: {
        user_id: function () {
            this.get_label_tasks(this.user_id);
            this.get_labels(this.label_task_id, this.user_id);
        },

        label_task_id: function () {
            this.get_labels(this.label_task_id, this.user_id);
        },

        input_data_id: function () {
            this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
        }
    }
};
</script>

<style>
/* .im { display: inline } */
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>