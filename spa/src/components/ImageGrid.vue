<template>
    <div>
        <div class="row">
          <div class="col"></div>

          <div class="col">
              <div class="row justify-content-center">
                <!-- <button v-on:click="get_label_options">Refresh label task list</button> -->

                <div class="col-md-12">
                    <!-- <span class="col-md-4 col-xs-6 im" v-for="uld in user_labeled_data_reversed" :key="uld.input_data_id" ><p>{{ uld.input_data_id }}</p> </span> -->
                    <ImageThumbnail class="col-md-4 col-xs-6 im" v-for="uld in user_labeled_data_reversed" :key="uld.input_data_id" v-bind:user-labeled-data="uld"> {{ uld.input_data_id }} </ImageThumbnail>
                </div>

              </div>
          </div>

          <div class="col"></div>
      </div>
    </div>
</template>

<script>
import ImageThumbnail from './ImageThumbnail'

import axios from "axios";

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
    name: "image_grid",
    data: function() {
        return {
            user_labeled_data: []
        };
    },
    computed: {
        label_task: function() {
            return this.$store.getters.label_task;
        },
        user_labeled_data_reversed: function() {
            return this.user_labeled_data.slice().reverse();
        }
    },
    components: {
        ImageThumbnail,
    },
    beforeMount() {
        this.get_data_labeled_by_user();
    },
    methods: {
        get_data_labeled_by_user: function() {
            // get list of past data labeled by user for this particular label task

            const vm = this;

            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            axios
                .get("all_data/label_tasks/" + this.label_task.label_task_id + "/users/own", config)
                .then(function(response) {
                    //   vm.label_tasks = response.data;

                    console.log(response.data)

                    vm.user_labeled_data = response.data;
                })
                .catch(function(error) {
                console.log(error);
                });
        },

        // select_label_task: function(label_task_id) {
        //     // store the list of label tasks in the global store so that it can be used by the image labeler component

        //     this.$store.commit('select_label_task', label_task_id);

        //     // go to other window to allow user to label images from this label task
        //     this.$router.push('image_labeler');
        // },

        // view_labeled_data: function(label_task_id) {
        //     // go to other window to allow user to view his/her images from this label task
        //     console.log("view_labeled_data:", label_task_id);
        // }
    }
};
</script>

<style>
.im { display: inline }
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>