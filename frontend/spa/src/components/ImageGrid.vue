<template>
    <div class="container">
        <div class="row">
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

                <!-- <div class="row justify-content-center filters-menu"> -->
                <div class=" filters-menu ">
                        <b-button-toolbar>
                            <b-input-group  size="md" class="w-25 mx-1" prepend="User complete">
                                <b-form-select v-model="filters.user_complete_selected" :options="filters.options"></b-form-select>
                            </b-input-group>
                            <b-input-group  size="md" class="w-25 mx-1" prepend="Needs improvement">
                                <b-form-select v-model="filters.needs_improvement_selected" :options="filters.options"></b-form-select>
                            </b-input-group>
                            <b-input-group  size="md" class="w-25 mx-1" prepend="Approved">
                                <b-form-select v-model="filters.admin_complete_selected" :options="filters.options"></b-form-select>
                            </b-input-group>
                            <b-input-group  size="md" class="w-25 mx-1" prepend="Paid">
                                <b-form-select v-model="filters.paid_selected" :options="filters.options"></b-form-select>
                            </b-input-group>
                        </b-button-toolbar>
                </div>

                <div class="row justify-content-center">
                    <div class="col-md-12" v-if="user_labeled_data.length > 0">
                        <ImageThumbnail class="col-md-4 col-xs-6 im" v-for="uld in user_labeled_data_pag" :key="uld.input_data_id" v-bind:user-labeled-data="uld"> {{ uld.input_data_id }} </ImageThumbnail>
                    </div>
                    <div v-else class="no-images-labeled">
                        <h6>No images labeled yet.</h6>
                        <h6>Click the <router-link v-bind:to="'/image_labeler'" >Labeler</router-link> tab to begin labeling images for this label task.</h6>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script>
import ImageThumbnail from './ImageThumbnail.vue'

import axios from "axios";
import { mapGetters } from 'vuex';

axios.defaults.baseURL = process.env.API_ADDR;

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
            page_number: 1,
            filters: {
                user_complete_selected: undefined,
                needs_improvement_selected: undefined,
                admin_complete_selected: undefined,
                paid_selected: undefined,
                options: [
                    { value: undefined, text: '' },
                    { value: true, text: 'Yes' },
                    { value: false, text: 'No' }
                ]
            }
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
            let a = this.user_labeled_data_reversed.filter(data => data.user_complete == this.filters.user_complete_selected || 
                                                                   this.filters.user_complete_selected == undefined);

            let b = a.filter(data => data.needs_improvement == this.filters.needs_improvement_selected || 
                                     this.filters.needs_improvement_selected == undefined);

            let c = b.filter(data => data.admin_complete == this.filters.admin_complete_selected || 
                                     this.filters.admin_complete_selected == undefined);

            let d = c.filter(data => data.paid == this.filters.paid_selected || 
                                     this.filters.paid_selected == undefined);

            return d;
        },
        user_labeled_data_pag: function () {
            return paginate (this.user_labeled_data_filt, this.page_size, this.page_number);
        },
        total_pages: function () {
            let total_pages = Math.ceil(this.user_labeled_data_filt.length / this.page_size);
            this.page_number = total_pages;
            return total_pages;
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
.im { display: inline;
      padding-top: 0.7em }
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