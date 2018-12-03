<template>
    <div class="container">
        <div class="row justify-content-center email-form">
            <label for="user_email"><b>Email</b></label>
            <input type="email" placeholder="Enter email address" name="user_email" required v-model="email">

            <label for="psw"><b>Password</b></label>
            <input type="password" placeholder="Enter password" name="psw" required v-model="password" v-on:keydown.enter="logUserIn">

            <button type="submit" v-on:click="logUserIn">Login</button>
        </div>
        <div id="auth_error_msg" class="row justify-content-center">
            <p v-if="authentication_error">Error authenticating user. Please re-enter log in details.</p>
        </div>
    </div>
</template>

<script>
import {  mapGetters } from "vuex";
import {  mapActions } from "vuex";

export default {
    name: "login",
    data: function() {
        return {
            email: null,
            password: null
        };
    },
    computed: {
        ...mapGetters('user_login', [
            'authentication_error'
        ])
    },
    methods: {
        ...mapActions('user_login', [
            'login',
            'get_user_id',
            'get_user_type'
        ]),
        logUserIn: function() {
            // get access token from server to permit user to make requests to the backend

            var vm = this;

            this.login({ email: this.email, password: this.password })
                .then(function(response) {
                    vm.get_user_id();
                })
                .then(function(response) {
                    vm.get_user_type();
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
.email-form { padding-top: 3em }
.email-form label { padding-left: 1.5em }
.email-form label { padding-right: 0.5em }
#auth_error_msg { padding-top: 3em }
/* #login {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>
