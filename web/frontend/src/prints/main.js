import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'

Vue.use(BootstrapVue)
Vue.use(VueSwal)
Vue.use(Sticky)

import PrintsPage from './PrintsPage.vue'
import PrintPage from './PrintPage.vue'

if (document.getElementById('prints-mount')) {
  new Vue({
    components: { PrintsPage }
  }).$mount('#prints-mount')
}

if (document.getElementById('print-mount')) {
  new Vue({
    components: { PrintPage }
  }).$mount('#print-mount')
}
