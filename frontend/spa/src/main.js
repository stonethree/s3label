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

import { StoreLogin } from './vuex_stores/login_store'
import { StoreLabelTask } from './vuex_stores/label_task_store'
import { StoreImageLabeling } from './vuex_stores/image_labeling_store'


Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(BootstrapVue)

Vue.config.productionTip = false


const store = new Vuex.Store({
    modules: {
        user_login: StoreLogin,
        label_task_store: StoreLabelTask,
        image_labeling: StoreImageLabeling
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
            if (store.getters['label_task_store/label_task'] == undefined) {
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
            if (store.getters['label_task_store/label_task'] == undefined) {
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
    if (store.getters['user_login/is_logged_in'] || to.path == '/login') {
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
