<template>
    <div class="container">
        <div class="row">
          <!-- <div class="col"></div> -->

          <div class="col">
              <div class="row justify-content-center">
                <button v-on:click="get_label_task_list">Refresh label task list</button>
              </div>
              <div v-for="lt in label_tasks" :key="lt.label_task_id">
                  <div class="card" style="background-color:hsla(20, 100%, 64%, 0.7);">
                      <div class="card-body">
                          <h4 class="card-title"> {{ lt.label_task_id }} - {{ lt.title }} </h4>
                          <h6 class="card-subtitle mb-2 font-italic"> {{ lt.type }} </h6>
                          <p> {{ lt.description }} </p>
                          <button v-on:click="choose_label_task(lt.label_task_id)"> Label data </button>
                          <button v-on:click="view_labeled_data(lt.label_task_id)"> View labeled data </button>
                      </div>
                  </div>
              </div>
          </div>

          <!-- <div class="col"></div> -->
      </div>
    </div>
</template>

<script>
import axios from "axios";
import { mapMutations, mapGetters } from 'vuex';

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
  name: "label_task_chooser",
  data: function() {
    return {
    };
  },
  computed: {
      ...mapGetters('label_task_store', [
        'label_tasks'
    ]),
  },
  beforeMount() {
        this.get_label_task_list();
    },
  methods: {
    ...mapMutations('label_task_store', [
        'set_label_tasks',
        'select_label_task'
    ]),
    get_label_task_list: function() {
      // get list of label tasks from the backend

      const vm = this;

      let access_token = localStorage.getItem("s3_access_token");

      let config = {
        headers: {
          Authorization: "Bearer " + access_token
        }
      };

      axios
        .get("label_tasks", config)
        .then(function(response) {
          var label_tasks = response.data;

          // store the list of label tasks in the global store so that it can be used by the image labeler component

          vm.set_label_tasks(label_tasks);
        })
        .catch(function(error) {
          console.log(error);
        });
    },
    choose_label_task: function(label_task_id) {
      // store the list of label tasks in the global store so that it can be used by the image labeler component
      this.select_label_task(label_task_id);

      // go to other window to allow user to label images from this label task
      this.$router.push('image_labeler');
    },
    view_labeled_data: function(label_task_id) {
      // go to other window to allow user to view his/her images from this label task

      this.select_label_task(label_task_id);

      // go to other window to allow user to label images from this label task
      
      this.$router.push('image_grid');
    }
  }
};
</script>

<style>
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>