<template>
    <div id="app" class="container-fluid">
        <div style="position: relative">
        <div class="row justify-content-center">
            <b-nav pills>
                <b-nav-item v-if="!is_logged_in" :to="'/login'" >Login</b-nav-item>
                <b-nav-item v-else :to="'/logout'">Logout</b-nav-item>
                <b-nav-item :to="'/label_tasks'" variant="secondary" :disabled="!is_logged_in">Tasks</b-nav-item>
                <b-nav-item :to="'/image_labeler'" :disabled="label_task_id==undefined || !is_logged_in">Label</b-nav-item>
                <b-nav-item :to="'/image_grid'" :disabled="label_task_id==undefined || !is_logged_in">Task Summary</b-nav-item>
                <b-nav-item v-if="is_admin_user && is_logged_in" :to="'/admin'">Admin</b-nav-item>
            </b-nav>
        </div>
        <div class="s3-logo">
            <b-img src="../static/stone-three-mining-logo_2.png"></b-img>
            <h1>S3 Label</h1>
        </div>
        <router-view></router-view>
    </div>
    </div>
</template>

<script>

import {  mapGetters } from "vuex";

export default {
    name: "App",
    computed: {
        ...mapGetters('user_login', [
            'is_logged_in',
            'is_admin_user'
        ]),
        ...mapGetters('label_task_store', [
            'label_task_id'
        ]),
    },
};
</script>

<style>
.s3-logo { position: absolute; 
           left: 0; 
           top: 0.7em }
img { display: inline }
h1 { display: inline }
a { color: #000 }
.nav { margin-bottom: 1.6em;
       margin-top: 0.7em; }
.nav-pills .nav-link.active, .nav-pills .show>.nav-link { color: #fff;
                                                          background-color: black}
/* #app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  margin-bottom: 160px;
} */
</style>
