import Vue from 'vue'
import Vuex from "vuex";
import App from './App'
import VueRouter from 'vue-router'

import Login from './components/Login'
import LabelTaskChooser from './components/LabelTaskChooser'
import ImageLabeler from './components/ImageLabeling'

Vue.use(VueRouter)
Vue.use(Vuex)

Vue.config.productionTip = false

const routes = [
  { path: '/', component: Login },
  { path: '/login', component: Login },
  { path: '/label_tasks', component: LabelTaskChooser },
  { path: '/image_labeler', component: ImageLabeler }
]

const router = new VueRouter({
  routes, // short for routes: routes
  mode: 'history'
})

// export default new Vuex.Store({

const store = new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    increment (state) {
      state.count++
    }
  }
})

console.log("console.log(store.state.count):", store.state.count)

/* eslint-disable no-new */
new Vue({
  el: '#app',           // define the selector for the root component
  template: '<App/>',   // pass the template to the root component
  components: { App },  // declare components that the root component can access
  store,
  router,
  render: h => h(App)
}).$mount('#app')       // mount the router on the app
