<template>
    <div class="container">
        <b-tabs>
            <b-tab title="Check Labeling Results" active>
                <br>
                <check-user-labeling></check-user-labeling>
            </b-tab>
            <b-tab title="Upload Input Data">
                <br>
                <upload-images></upload-images>
                </b-tab>
        </b-tabs>
    </div>
</template>

<script>

import CheckUserLabeling from './CheckUserLabeling.vue'
import UploadImages from './UploadImages.vue'

export default {
    name: "admin_view",
    data: function() {
        return {
        };
    },
    components: {
        CheckUserLabeling,
        UploadImages
    },
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
