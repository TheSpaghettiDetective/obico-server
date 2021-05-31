import Vue from 'vue'
import VueSwal from 'common/VueSwal'

import OctoPrintTunnelPage from './OctoPrintTunnelPage.vue'
import setupSentry from '@lib/sentry'
import { initTheme } from '../main/themes.js'

initTheme()
setupSentry(Vue)
Vue.use(VueSwal)

new Vue({
  components: { OctoPrintTunnelPage }
}).$mount('#octoprint-tunnel-mount')
