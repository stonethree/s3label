import Vue from 'vue'
import App from './App'
import VueRouter from 'vue-router'

import Hello from './components/HelloWorld'
import About from './components/About'

Vue.use(VueRouter)

Vue.config.productionTip = false

const routes = [
  { path: '/', component: Hello },
  { path: '/about', component: About }
]

const router = new VueRouter({
  routes, // short for routes: routes
  mode: 'history'
})

/* eslint-disable no-new */
new Vue({
  el: '#app',           // define the selector for the root component
  template: '<App/>',   // pass the template to the root component
  components: { App },  // declare components that the root component can access
  router,
  render: h => h(App)
}).$mount('#app')       // mount the router on the app
