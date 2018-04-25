<template>
  <div id="app">
    <div class="row justify-content-center">
      <h1>S3 Label</h1>
    </div>
    <div class="row">
      <div class="col"></div>
      <div class="col">
        <nav class="navbar">
        <ul class="nav justify-content-center nav-justified">
          <li v-if="!user_logged_in" class="nav-item ">
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
        </ul>
        </nav>
      </div>
      <div class="col"></div>
    </div>
    <!-- the router outlet, where all matched components will be viewed -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "App",
  computed: {
        user_logged_in: function() {
            return this.$store.getters.logged_in;
        }
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
