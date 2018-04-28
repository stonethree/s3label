<template>
  <div id="app" class="container-fluid">
    <div class="row justify-content-center">
      <h1>S3 Label</h1>
    </div>
    <div class="row justify-content-center">
      <!-- <div class="col"></div> -->
      <!-- <div class="col"> -->
        <nav class="navbar">
        <ul class="nav justify-content-center nav-justified">
          <li v-if="!is_logged_in" class="nav-item ">
            <router-link v-bind:to="'/login'" class="nav-link ">Login</router-link>
          </li>
          <li v-else class="nav-item ">
            <router-link v-bind:to="'/logout'" class="nav-link ">Logout</router-link>
          </li>
          <li class="nav-item">
            <router-link v-bind:to="'/label_tasks'" class="nav-link ">Label Tasks</router-link>
          </li>
          <li class="nav-item">
            <router-link v-bind:to="'/image_labeler'" class="nav-link ">Labeler</router-link>
          </li>
          <li class="nav-item">
            <router-link v-bind:to="'/image_grid'" class="nav-link ">Image Grid</router-link>
          </li>
          <li class="nav-item">
            <router-link v-bind:to="'/admin'" class="nav-link ">Admin</router-link>
          </li>
          <!-- <i class="fa fa-camera"></i>
          <i class="fa fa-circle"></i>
          <i class="fa fa-circle-thin"></i>
          <i class="fa fa-address-book"></i>
          <i class="fa fa-check"></i>
          <i class="fa fa-check-circle"></i>
          <i class="fa fa-check-square"></i>
          <i class="fa fa-check-square-o"></i>
          <i class="fa fa-caret-down"></i>
          <i class="fa fa-caret-up"></i>
          <i class="fa fa-angle-up"></i>
          <i class="fa fa-angle-down"></i>
          <i class="fa fa-angle-left"></i>
          <i class="fa fa-angle-right"></i>
          <i class="fa fa-at"></i>
          <i class="fa fa-comment"></i>
          <i class="fa fa-commenting"></i>
          <i class="fa fa-commenting-o"></i>
          <i class="fa fa-comments"></i>
          <i class="fa fa-comments-o"></i>
          <i class="fa fa-credit-card"></i>
          <i class="fa fa-dollar-sign"></i>
          <i class="fa fa-dollar"></i>
          <i class="fa fa-edit"></i>
          <i class="fa fa-envelope"></i>
          <i class="fa fa-envelope-o"></i>
          <i class="fa fa-envelope-open"></i>
          <i class="fa fa-envelope-open-o"></i>
          <i class="fa fa-flag"></i>
          <i class="fa fa-flag-o"></i>
          <i class="fa fa-folder"></i>
          <i class="fa fa-home"></i>
          <i class="fa fa-info"></i>
          <i class="fa fa-info-circle"></i>
          <i class="fa fa-keyboard"></i>
          <i class="fa fa-keyboard-o"></i>
          <i class="fa fa-lightbulb"></i>
          <i class="fa fa-lock"></i>
          <i class="fa fa-unlock"></i>
          <i class="fa fa-pencil"></i>
          <i class="fa fa-pen-square"></i>
          <i class="fa fa-pen-square-o"></i>
          <i class="fa fa-phone"></i>
          <i class="fa fa-phone-square"></i>
          <i class="fa fa-question"></i>
          <i class="fa fa-question-circle"></i>
          <i class="fa fa-search"></i>
          <i class="fa fa-search-minus"></i>
          <i class="fa fa-search-plus"></i>
          <i class="fa fa-spinner"></i>
          <div>
          <i class="fa fa-spinner fa-spin"></i>
          </div>
          <div>
          <i class="fa fa-spinner fa-pulse"></i>
          </div>
          <i class="fa fa-square"></i>
          <i class="fa fa-square-o"></i>
          <i class="fa fa-tasks"></i>
          <i class="fa fa-th"></i>
          <i class="fa fa-th-list"></i>
          <i class="fa fa-tag"></i>
          <i class="fa fa-tags"></i>
          <i class="fa fa-thumbs-up"></i>
          <i class="fa fa-thumbs-o-up"></i>
          <i class="fa fa-thumbs-down"></i>
          <i class="fa fa-thumbs-o-down"></i>
          <i class="fa fa-toggle-off"></i>
          <i class="fa fa-toggle-on"></i>
          <i class="fa fa-trash"></i>
          <i class="fa fa-trash-o"></i>
          <i class="fa fa-trash-alt"></i>
          <i class="fa fa-user"></i>
          <i class="fa fa-user-o"></i>
          <i class="fa fa-user-circle"></i>
          <i class="fa fa-users"></i>
          <i class="fa fa-user-secret"></i>
          <i class="fa fa-wrench"></i> -->
          <!-- <i class="fa fa-dollars"></i> -->
        </ul>
        </nav>
      </div>
      <!-- <div class="col"></div> -->
    <!-- </div> -->
    <!-- the router outlet, where all matched components will be viewed -->
    <router-view></router-view>
  </div>
</template>

<script>

import {  mapGetters } from "vuex";

export default {
    name: "App",
    computed: {
        ...mapGetters([
            'is_logged_in'
        ])
    },
};
</script>

<style>
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
