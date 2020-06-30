import Vue from 'vue'
import { BootstrapVue} from 'bootstrap-vue'
import App from './App.vue'

Vue.use(BootstrapVue)

new Vue({
  render: h => h(App),
}).$mount('#vue-app-simple')
