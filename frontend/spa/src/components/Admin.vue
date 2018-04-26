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
                    <b-table striped hover :items="labeled_input_data" small @row-clicked="select_label"></b-table>
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

function convertPolygonToPaths(polygon) {
    return polygon.regions;
}

export default {
    name: "admin_view",
    data: function() {
        return {
            user_id: undefined,
            label_task_id: undefined,
            label_id: undefined,
            users: undefined,
            label_tasks: undefined,
            labeled_input_data: undefined,
            input_data_id: undefined,
            padX: 80,
            padY: 80,
            polygons: [],
            lineWidth: 2,
            opacity: 0.3,
            stroke_thickness: 2,
            use_stroke: true,
        };
    },

    beforeMount() {
        this.get_users();
    },

    computed: {
        ctx: function() {
            let canvas_fg = document.getElementById("canvas-fg");
            return canvas_fg.getContext("2d");
        },
        label_task: function() {
            if (this.label_task_id != undefined) {
                return this.label_tasks[this.label_task_id];
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
                    d[this.labels[i].label_class] = this.extractColor(this.labels[i].color);
                }
                return d;
            }
            else {
                return null
            }
        }
    },

    watch: {
        user_id: function () {
            this.get_label_tasks_for_user(this.user_id);
            this.get_labeled_input_data(this.label_task_id, this.user_id);
        },

        label_task_id: function () {
            this.get_labeled_input_data(this.label_task_id, this.user_id);
        },

        input_data_id: function () {
            this.fetchAndDisplayImage(baseUrl + '/input_images/' + this.input_data_id);
            this.loadImageLabels(this.input_data_id);
        }
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
                    console.log(response.data)

                    vm.label_tasks = response.data;
                })
                .catch(function(error) {
                    console.log(error);
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
                    })
                    .catch(function(error) {
                        console.log(error);
                    });
            }
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

        // polygon drawing functions

        drawAllPolygons: function (context, polygon_list) {
            context.lineWidth = this.stroke_thickness;
            context.clearRect(0, 0, context.canvas.width, context.canvas.height);

            for (let i = 0; i < polygon_list.length; i++) {
                this.drawPolygon(context, polygon_list[i]);
            }
        },

        drawPolygon: function (context, polygon) {
            this.setColor(this.label_colors[polygon.label], this.opacity);
            let paths_to_draw = convertPolygonToPaths(polygon.polygon);

            if (polygon.selected) {
                // draw selected polygon

                var currentStrokeStyle = context.strokeStyle;
                context.strokeStyle = "#FF0000";
                context.setLineDash([4, 4]);

                for (let j = 0; j < paths_to_draw.length; j++) {
                    this.drawPath(context, paths_to_draw[j]);
                }

                context.strokeStyle = currentStrokeStyle;
                context.setLineDash([]);
            }
            else {
                // draw unselected polygon

                for (let j = 0; j < paths_to_draw.length; j++) {
                    this.drawPath(context, paths_to_draw[j]);
                }
            }
        },

        drawPath: function (context, path) {

            let w = context.canvas.width;
            let h = context.canvas.height;

            context.beginPath();
            context.moveTo(Math.max(this.padX, Math.min(path[0][0], w - this.padX)),
                Math.max(this.padY, Math.min(path[0][1], h - this.padY)));

            for (let i = 1; i < path.length; i++) {
                context.lineTo(Math.max(this.padX, Math.min(path[i][0], w - this.padX)),
                    Math.max(this.padY, Math.min(path[i][1], h - this.padY)));
            }

            context.closePath();
            if (this.use_stroke) {
                context.stroke();
            }
            context.fill();
        },

        extractColor: function (rgb_string) {
            // takes a string of format
            var rgb = JSON.parse(rgb_string)

            if (rgb.length == 3) {
                return rgb;
            }
            else {
                throw TypeError('Color string must have 3 RGB elements specified');
            }
        },

        formatColor: function (rgb, alpha) {
            return 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',' + alpha + ')';
        },

        setColor: function (rgb, alpha) {
            this.ctx.fillStyle = this.formatColor(rgb, alpha);
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
                .get("labels/input_data/" + input_data_id + "/label_tasks/" + this.label_task_id, config)
                .then(function(response) {
                    if (response.data.length == 1) {
                        console.log("Label found for this image: attempting to apply it in the view")
                        let label = response.data[0];

                        // check label format is correct

                        var polygons = JSON.parse(label.label_serialised);

                        if (polygons.length > 0 && polygons[0].polygon != undefined) {
                            console.log('Applied serialised label to image')
                            vm.polygons = polygons;
                            vm.drawAllPolygons(vm.ctx, vm.polygons);
                        }
                        else {
                            console.log('Serialised label has wrong format:', polygons)
                        }
                    }
                    else if (response.data.length == 0) {
                        console.log("No label found for this image")
                    }
                    else {
                        console.log("Error: expected at most one label for this image!")
                    }
                })
                .catch(function(error) {
                    console.log(error);
                });
        },
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