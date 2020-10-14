import Vue from 'vue'
import VueSwal from 'common/VueSwal'

import OctoPrintTunnelPage from './OctoPrintTunnelPage.vue'

Vue.use(VueSwal)

new Vue({
  components: { OctoPrintTunnelPage }
}).$mount('#octoprint-tunnel-mount')
