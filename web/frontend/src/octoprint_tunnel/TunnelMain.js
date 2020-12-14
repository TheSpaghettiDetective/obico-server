import Vue from 'vue'
import VueSwal from 'common/VueSwal'

import OctoPrintTunnelPage from './OctoPrintTunnelPage.vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(VueSwal)

new Vue({
  components: { OctoPrintTunnelPage }
}).$mount('#octoprint-tunnel-mount')
