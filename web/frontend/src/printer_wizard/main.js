import Vue from 'vue'
import { BootstrapVue} from 'bootstrap-vue'
import App from './PrinterWizardPage.vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(BootstrapVue)

new Vue({
  render: h => h(App),
}).$mount('#printer_wizard-app')
