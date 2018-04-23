<template>
    <div class="container">
      <div class="row justify-content-center">
        <label for="user_email"><b>Email</b></label>
        <input type="email" placeholder="Enter email address" name="user_email" required v-model="email">

        <label for="psw"><b>Password</b></label>
        <input type="password" placeholder="Enter password" name="psw" required v-model="password">

        <button type="submit" v-on:click="logUserIn">Login</button>
      </div>
      <div id="auth_error_msg" class="row">
          <p v-if="authentication_error">Error authenticating user. Please re-enter log in details.</p>
      </div>
    </div>
</template>

<script>
import axios from 'axios';

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
    
  name: "login",
  data: function() {
    return {
      email: null,
      password: null,
      authentication_error: false,
    };
  },
  computed: {
    userIsLoggedIn: function() {
      return !(localStorage.s3_access_token === undefined);
    }
  },
  methods: {
    logUserIn: function() {
      // get access token from server to permit user to make requests to the backend

      const vm = this;

      axios
        .post("login", {
          email: vm.email,
          password: vm.password
        })
        .then(function(response) {
          var access_token = response.data.access_token;

          // store access token in localStorage
          localStorage.setItem("s3_access_token", access_token);

          vm.$store.commit('login');

          console.log("User logged in successfully");
          vm.authentication_error = false;

          vm.$router.push('label_tasks');
        })
        .catch(function(error) {
          console.log("Log in unsuccessful:", error);
          vm.authentication_error = true;
        });
    }
  }
};
</script>

<style>
/* #login {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>
