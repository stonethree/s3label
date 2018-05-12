<template>
    <div class="container">
        <div class="row">
          <!-- <div class="col"></div> -->

        <div class="col">
            <div class="row justify-content-center pagination-menu">
                <nav aria-label="...">
                    <ul class="pagination">
                        <li class="page-item" v-bind:class="{ disabled: page_number==1 }" @click="previous_page">
                            <a class="page-link" href="#" >Previous</a>
                        </li>
                        <li class="page-item" v-bind:class="{ active: page_num==page_number }" v-for="page_num in total_pages" :key="page_num" @click="page_number = page_num">
                            <a class="page-link" href="#">{{ page_num }}</a>
                        </li>
                        <li class="page-item" v-bind:class="{ disabled: page_number==total_pages }" @click="next_page">
                            <a class="page-link" href="#">Next</a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div class="row justify-content-center">

            <div class="col-md-12" v-if="user_labeled_data.length > 0">
                <ImageThumbnail class="col-md-4 col-xs-6 im" v-for="uld in user_labeled_data_filt" :key="uld.input_data_id" v-bind:user-labeled-data="uld"> {{ uld.input_data_id }} </ImageThumbnail>
            </div>
            <div v-else class="no-images-labeled">
                <h6>No images labeled yet.</h6>
                <h6>Click the <router-link v-bind:to="'/image_labeler'" >Labeler</router-link> tab to begin labeling images for this label task.</h6>
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

function paginate (array, page_size, page_number) {
    --page_number; // because pages logically start with 1, but technically with 0
    return array.slice(page_number * page_size, (page_number + 1) * page_size);
}

export default {
    name: "image_grid",
    data: function() {
        return {
            user_labeled_data: [],
            page_size: 6,
            page_number: 1
        };
    },
    computed: {
        ...mapGetters('label_task_store', [
            'label_task'
        ]),
        user_labeled_data_reversed: function() {
            return this.user_labeled_data.slice().reverse();
        },
        user_labeled_data_filt: function () {
            return paginate (this.user_labeled_data_reversed, this.page_size, this.page_number);
        },
        total_pages: function () {
            return Math.ceil(this.user_labeled_data.length / this.page_size);
        }
    },
    components: {
        ImageThumbnail,
    },
    beforeMount() {
        this.get_data_labeled_by_user();
    },
    methods: {
        next_page: function () {
            if (this.page_number < this.total_pages) {
                this.page_number ++;
            }
        },
        previous_page: function () {
            if (this.page_number > 1) {
                this.page_number --;
            }
        },
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
.no-images-labeled { padding-top: 2em }
.page-link { color: #000 }
.page-item.active .page-link { 
    color: #fff;
    background-color: #000;
    border-color: #000;
    }
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>