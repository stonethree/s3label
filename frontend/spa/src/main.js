import Vue from 'vue'
import Vuex from "vuex";
import App from './App'
import VueRouter from 'vue-router'
import BootstrapVue from 'bootstrap-vue'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'font-awesome/css/font-awesome.css'

import Login from './components/Login'
import Logout from './components/Logout'
import LabelTaskChooser from './components/LabelTaskChooser'
import ImageLabeler from './components/ImageLabeling'
import ImageGrid from './components/ImageGrid'
import Admin from './components/Admin'


Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(BootstrapVue)

Vue.config.productionTip = false


import axios from 'axios';

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

const ATTEMPT_LOGIN = 'attempt_login';
const LOGGED_IN = 'logged_in';
const LOGGED_OUT = 'logged_out';
const SET_USER_ID = 'set_user_id';
const SET_AUTHENTICATION_ERROR = 'set_authentication_error';

const storeLogin = {
    state: {
        is_logged_in: false, //!!localStorage.getItem("s3_access_token"),
        pending: false,
        user_id: undefined,
        authentication_error: false
    },
    mutations: {
        [ATTEMPT_LOGIN] (state) {
            state.is_logged_in = false;
            state.pending = true;
        },
        [LOGGED_IN] (state) {
            state.is_logged_in = true;
            state.pending = false;
            state.authentication_error = false;
        },
        [LOGGED_OUT] (state) {
            state.is_logged_in = false;
            state.pending = false;
        },
        [SET_USER_ID] (state, user_id) {
            state.user_id = user_id;
        },
        [SET_AUTHENTICATION_ERROR] (state, error_occured) {
            state.authentication_error = error_occured;
        },
    },
    actions: {
        async login({ commit }, credentials) {
            commit(ATTEMPT_LOGIN)

            // attempting to log in. Can display a spinner during this period to notify user to be patient

            await axios
            .post("login", {
                email: credentials.email,
                password: credentials.password
            })
            .then(function(response) {
                var access_token = response.data.access_token;

                // store access token in localStorage
                localStorage.setItem("s3_access_token", access_token)

                commit(LOGGED_IN)
            })
            .catch(function(error) {
                console.log("Log in unsuccessful:", error)
                commit(SET_AUTHENTICATION_ERROR, true)
                commit(LOGGED_OUT)
            })
        },
        async get_user_id({ commit }) {
            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            await axios
            .get("user_id", config)
            .then(function(response) {
                commit(SET_USER_ID, response.data.user_id)
            })
            .catch(function(error) {
                console.log("Could not get user ID:", error)
            })
        },
        logout({ commit }) {
            // remove access token from server to prevent user to making further requests to the backend
            localStorage.removeItem("s3_access_token")
            commit(LOGGED_OUT)
        }
    },
    getters: {
        is_logged_in: state => {
            return state.is_logged_in;
        },
        user_id: state => {
            return state.user_id;
        },
        authentication_error: state => {
            return state.authentication_error;
        }
    }
}


const store = new Vuex.Store({
    modules: {
        user_login: storeLogin
    },
    state: {
        label_tasks: [],
        label_task_id: -1
    },
    mutations: {
        set_label_tasks(state, label_tasks) {
            state.label_tasks = label_tasks;
        },
        select_label_task(state, idx) {
            state.label_task_id = idx;
        },
    },
    getters: {
        label_task: state => {
            return state.label_tasks.find(label_task => label_task.label_task_id === state.label_task_id)
        }
    }
})

const routes = [
    { path: '/', component: Login },
    { path: '/login', component: Login },
    { path: '/logout', component: Logout },
    { path: '/label_tasks', component: LabelTaskChooser },
    {
        path: '/image_labeler', name: 'image_labeler', component: ImageLabeler, props: true,
        beforeEnter: (to, from, next) => {
            // redirect to label task chooser if no label task yet specified
            if (store.getters.label_task == undefined) {
                next('/label_tasks')
            }
            else {
                next()
            }
        }
    },
    {
        path: '/image_grid', component: ImageGrid,
        beforeEnter: (to, from, next) => {
            // redirect to label task chooser if no label task yet specified
            if (store.getters.label_task == undefined) {
                next('/label_tasks')
            }
            else {
                next()
            }
        }
    },
    { path: '/admin', component: Admin }
]

const router = new VueRouter({
    routes, // short for routes: routes
    mode: 'history'
})


// reroute user to login page if not currently logged in

router.beforeEach((to, from, next) => {
    if (store.getters.is_logged_in || to.path == '/login') {
        next()
    }
    else {
        next('/login')
    }
})

/* eslint-disable no-new */
new Vue({
    el: '#app',           // define the selector for the root component
    template: '<App/>',   // pass the template to the root component
    components: { App },  // declare components that the root component can access
    store,
    router,
    render: h => h(App)
}).$mount('#app')       // mount the router on the app
