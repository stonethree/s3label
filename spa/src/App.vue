<template>
  <div id="app">
    <h1>S3 Label</h1>


    <div class="row">
      <div class="col"></div>
      <div class="col">
        <ul class="nav justify-content-center nav-justified">
          <li class="nav-item">
            <router-link v-bind:to="'/login'">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link v-bind:to="'/label_tasks'">Label Task Chooser</router-link>
          </li>
        </ul>
      </div>
      <div class="col"></div>
    </div>
    <!-- the router outlet, where all matched components will be viewed -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
