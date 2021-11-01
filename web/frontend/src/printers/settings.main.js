import Vue from 'vue'
import VueSwal from '@common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import setupSentry from '@lib/sentry'
import { initTheme } from '@main/colors'

initTheme()
setupSentry(Vue)
Vue.use(BootstrapVue)
Vue.use(VueSwal)

import PrinterSettingsPage from './PrinterSettingsPage.vue'

if (document.getElementById('printer-settings-mount')) {
  new Vue({
    components: { PrinterSettingsPage }
  }).$mount('#printer-settings-mount')
}
