import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'

Vue.use(BootstrapVue)
Vue.use(VueSwal)

import PrinterListPage from './PrinterListPage.vue'

new Vue({
  components: { PrinterListPage }
}).$mount('#printer-list-mount')
