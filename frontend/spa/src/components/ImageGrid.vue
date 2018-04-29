<template>
    <div class="container">
        <div class="row">
          <!-- <div class="col"></div> -->

          <div class="col">
              <div class="row justify-content-center">

                <div class="col-md-12">
                    <ImageThumbnail class="col-md-4 col-xs-6 im" v-for="uld in user_labeled_data_reversed" :key="uld.input_data_id" v-bind:user-labeled-data="uld"> {{ uld.input_data_id }} </ImageThumbnail>
                </div>

              </div>
          </div>

          <!-- <div class="col"></div> -->
      </div>
    </div>
</template>

<script>
import ImageThumbnail from './ImageThumbnail'

import axios from "axios";
import { mapGetters } from 'vuex';

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
    name: "image_grid",
    data: function() {
        return {
            user_labeled_data: []
        };
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task'
        ]),
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
                    console.log(response.data)

                    vm.user_labeled_data = response.data;
                })
                .catch(function(error) {
                console.log(error);
                });
        },
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