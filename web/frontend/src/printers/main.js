import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import setupSentry from '@lib/sentry'
import { initTheme } from '@main/themes'
import VuePluralize from 'vue-pluralize'

initTheme()
setupSentry(Vue)
Vue.use(BootstrapVue)
Vue.use(VueSwal)
Vue.use(VuePluralize)

import PrinterListPage from './PrinterListPage.vue'
import SharedPrinterPage from './SharedPrinterPage.vue'
import PrinterSettingsPage from './PrinterSettingsPage.vue'
import PrinterWizardPage from './PrinterWizardPage.vue'
import PrinterControlPage from './PrinterControlPage.vue'
import SharePrinter from './SharePrinter.vue'
import GCodesPage from './GCodesPage.vue'


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

if (document.getElementById('printer-settings-mount')) {
  new Vue({
    components: { PrinterSettingsPage }
  }).$mount('#printer-settings-mount')
}

if (document.getElementById('printer-wizard-mount')) {
  new Vue({
    components: { PrinterWizardPage }
  }).$mount('#printer-wizard-mount')
}

if (document.getElementById('printer-control-mount')) {
  new Vue({
    components: { PrinterControlPage }
  }).$mount('#printer-control-mount')
}

if (document.getElementById('share-printer-mount')) {
  new Vue({
    components: { SharePrinter }
  }).$mount('#share-printer-mount')
}

if (document.getElementById('gcodes-page-mount')) {
  new Vue({
    components: { GCodesPage }
  }).$mount('#gcodes-page-mount')
}
