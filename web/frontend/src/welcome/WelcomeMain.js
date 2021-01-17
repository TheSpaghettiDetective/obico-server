import Vue from 'vue'
import { BootstrapVue} from 'bootstrap-vue'
import App from './App.vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(BootstrapVue)

new Vue({
  render: h => h(App),
}).$mount('#welcome-app')
