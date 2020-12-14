import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(BootstrapVue)
Vue.use(VueSwal)

import PrinterListPage from './PrinterListPage.vue'
import SharedPrinterPage from './SharedPrinterPage.vue'

if (document.getElementById('printer-list-mount')) {
  new Vue({
    components: { PrinterListPage }
  }).$mount('#printer-list-mount')
}

if (document.getElementById('shared-printer-mount')) {
  new Vue({
    components: { SharedPrinterPage }
  }).$mount('#shared-printer-mount')
}
