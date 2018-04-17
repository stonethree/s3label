<template>
    <div class="container">
      <label for="user_email"><b>Email</b></label>
      <input type="email" placeholder="Enter email address" name="user_email" required v-model="email">

      <label for="psw"><b>Password</b></label>
      <input type="password" placeholder="Enter password" name="psw" required v-model="password">

      <button type="submit" v-on:click="logUserIn">"Login"</button>
    </div>
</template>

<script>
axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

export default {
  name: "about",
  data: function() {
    return {
      email: null,
      password: null
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

          console.log("User logged in successfully");
        })
        .catch(function(error) {
          console.log("Log in unsuccessful:", error);
        });
    }
  }
};
</script>

<style>
#about {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
