<template>
    <div class="container status-icons">
        <div @click="toggle_user_complete">
            <span v-if="status.user_complete" class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.user_complete.marked">
                <i class="fa fa-user-o fa-stack-1x"></i>
                <i class="fa fa-check fa-stack-1x tick"></i>
            </span>
            <span v-else class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.user_complete.unmarked">
                <i class="fa fa-user-o fa-stack-1x icon-dim"></i>
            </span>
        </div>
        <div @click="toggle_needs_improvement">
            <span v-if="status.needs_improvement" class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.needs_improvement.marked">
                <i class="fa fa-flag fa-stack-1x"></i>
                <i class="fa fa-times fa-stack-1x cross"></i>
                <!-- <i class="fa fa-exclamation-circle"></i> -->
                <!-- <i class="fa fa-exclamation-triangle"></i> -->
            </span>
            <span v-else class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.needs_improvement.unmarked">
                <i class="fa fa-flag fa-stack-1x icon-dim"></i>
            </span>
        </div>
        <div @click="toggle_admin_complete">
            <span v-if="status.admin_complete" class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.admin_complete.marked">
                <i class="fa fa-check fa-stack-1x tick"></i>
                <i class="fa fa-smile-o fa-stack-1x"></i>
            </span>
            <span v-else class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.admin_complete.unmarked">
                <i class="fa fa-smile-o fa-stack-1x icon-dim"></i>
            </span>
        </div>
            <div @click="toggle_paid">
            <span v-if="status.paid" class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.paid.marked">
                <i class="fa fa-check fa-stack-1x tick"></i>
                <i class="fa fa-dollar fa-stack-1x"></i>
            </span>
            <span v-else class="fa-stack" data-toggle="tooltip" v-bind:title="tooltips.paid.unmarked">
                <i class="fa fa-dollar fa-stack-1x icon-dim"></i>
            </span>
        </div>
    </div>
</template>

<script>
import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

const tooltips_all = {
    user_mode: {
        user_complete: {
            marked: "Click or <Ctrl+Enter> to unmark 'labeling complete' for this image",
            unmarked: "Click or <Ctrl+Enter> to mark 'labeling complete' for this image"
        },
        needs_improvement: {
            marked: "This image needs more labeling before it can be declared 'complete'!",
            unmarked: ""
        },
        admin_complete: {
            marked: "This image has been declared 'complete' by an admin user! Thank you and well done!",
            unmarked: "This image has not yet been declared 'complete' by an admin user"
        },
        paid: {
            marked: "You have been paid for labeling this image",
            unmarked: "You have not yet been paid for this image"
        },
    },
    admin_mode: {
        user_complete: {
            marked: "Click or <Ctrl+Enter> to unmark 'user labeling complete status' for this image",
            unmarked: "Click or <Ctrl+Enter> to mark 'user labeling complete status' for this image"
        },
        needs_improvement: {
            marked: "Click to unmark 'needs improvement to the labeling' for this image",
            unmarked: "Click to mark 'needs improvement to the labeling' for this image"
        },
        admin_complete: {
            marked: "Click to unmark 'admin user satisfied' for this image",
            unmarked: "Click to mark 'admin user satisfied' for this image"
        },
        paid: {
            marked: "Click to set status to 'paid' for this image",
            unmarked: "Click to set status to 'paid' for this image"
        },
    }
    
};

export default {
    name: "label_status",
    props: {
        userCompletedToggle: {
            type: Boolean,
            default: false
        }, 
        needsImprovementToggle: {
            type: Boolean,
            default: false
        }, 
        adminCompletedToggle: {
            type: Boolean,
            default: false
        }, 
        paidToggle: {
            type: Boolean,
            default: false
        }, 
        mode: {
            type: String,
            default: 'user_mode',
            validator: function(value) {
                return ['admin_mode', 'user_mode'].indexOf(value) !== -1
            }
        },
    },
    data: function() {
        return {
            status: {
                user_complete: true,
                needs_improvement: false,
                admin_complete: false,
                paid: false,
            }
        };
    },
    computed: {
        tooltips: function () {
            return tooltips_all[this.mode];
        }
    },
    beforeMount() {
        // this.fetchAndDisplayImage(this.image_request_path);
    },
    watch: {
        userCompletedToggle: function() {
            this.toggle_user_complete();
        },
        needsImprovementToggle: function() {
            this.toggle_needs_improvement();
        },
        adminCompletedToggle: function() {
            this.toggle_admin_complete();
        },
        paidToggle: function() {
            this.toggle_paid();
        }
    },

    methods: {
        toggle_user_complete: function() {
            this.status.user_complete = !this.status.user_complete;
        },
        toggle_needs_improvement: function() {
            this.status.needs_improvement = !this.status.needs_improvement;
        },
        toggle_admin_complete: function() {
            this.status.admin_complete = !this.status.admin_complete;
        },
        toggle_paid: function() {
            this.status.paid = !this.status.paid;
        },
    }
};
</script>

<style>
.status-icons div { display: inline;
                    cursor: pointer;
                    padding-right: 1.5em; }
.tick { color:green;
            top: -1.4em;
            left: 0.8em;
            font-size: .7em }
.cross { color:rgb(182, 2, 2);
            top: -1.4em;
            left: 0.8em;
            font-size: .7em }
.icon-dim { color:rgb(189, 189, 189); }
/* .canvasesdiv canvas { display: inline } */
/* #label_task_chooser {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>