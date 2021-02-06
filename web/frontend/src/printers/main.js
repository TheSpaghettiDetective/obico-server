import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(BootstrapVue)
Vue.use(VueSwal)

import Navbar from '../common/Navbar.vue'

import PrinterListPage from './PrinterListPage.vue'
import SharedPrinterPage from './SharedPrinterPage.vue'
import PrinterSettingsPage from './PrinterSettingsPage.vue'
import PrinterWizardPage from './PrinterWizardPage.vue'

if (document.getElementById('navbar-mount')) {
  new Vue({
    components: { Navbar }
  }).$mount('#navbar-mount')
}

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
