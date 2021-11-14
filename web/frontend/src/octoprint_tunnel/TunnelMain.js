import Vue from 'vue'
import VueSwal from '@common/VueSwal'

import setupSentry from '@lib/sentry'
import { initTheme } from '@main/colors'
import { BootstrapVue } from 'bootstrap-vue'

initTheme()
setupSentry(Vue)
Vue.use(VueSwal)
Vue.use(BootstrapVue)

import NewOctoPrintTunnelPage from './NewOctoPrintTunnelPage.vue'
if (document.getElementById('new-octoprint-tunnel-mount')) {
  new Vue({
    components: { NewOctoPrintTunnelPage }
  }).$mount('#new-octoprint-tunnel-mount')
}

import OctoPrintTunnelPage from './OctoPrintTunnelPage.vue'
if (document.getElementById('octoprint-tunnel-mount')) {
  new Vue({
    components: { OctoPrintTunnelPage }
  }).$mount('#octoprint-tunnel-mount')
}
