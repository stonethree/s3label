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


const store = new Vuex.Store({
  state: {
    label_tasks: [],
    selected_label_task_id: -1,
    is_logged_in: false
  },
  mutations: {
    set_label_tasks (state, label_tasks) {
      state.label_tasks = label_tasks;
    },
    select_label_task (state, idx) {
      state.selected_label_task_id = idx;
    },

    login (state) {
      state.is_logged_in = true;
    },
    logout (state) {
      state.is_logged_in = false;
    },
  },
  getters: {
    label_task: state => {
      return state.label_tasks.find(label_task => label_task.label_task_id === state.selected_label_task_id)
    },

    logged_in: state => {
      return state.is_logged_in;
    }
  }
})

const routes = [
  { path: '/', component: Login },
  { path: '/login', component: Login },
  { path: '/logout', component: Logout },
  { path: '/label_tasks', component: LabelTaskChooser },
  { path: '/image_labeler', name: 'image_labeler', component: ImageLabeler, props: true, 
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
  { path: '/image_grid', component: ImageGrid, 
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
  if (store.getters.logged_in || to.path == '/login') {
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
