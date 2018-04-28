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
// import axios from "axios";

// axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

import {  mapGetters } from "vuex";



export default {
    name: "login",
    data: function() {
        return {
            email: null,
            password: null
        };
    },
    computed: {
        ...mapGetters([
            'authentication_error'
        ])
    },
    methods: {
        logUserIn: function() {
            // get access token from server to permit user to make requests to the backend

            var vm = this;

            this.$store
                .dispatch("login", { email: this.email, password: this.password })
                .then(function(response) {
                    vm.$store.dispatch("get_user_id");
                })
                .then(function(response) {
                    vm.$router.push('label_tasks');
                })
                .catch(function(error) {
                    console.log("Log in unsuccessful:", error)
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
