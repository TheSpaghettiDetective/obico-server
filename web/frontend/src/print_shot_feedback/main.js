import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import setupSentry from '@lib/sentry'
import { initTheme } from '@main/themes'

initTheme()
setupSentry(Vue)
Vue.use(VueSwal)
Vue.use(BootstrapVue)

import App from './PrintShotFeedbackApp.vue'

new Vue({
  components: { App }
}).$mount('#print-shot-feedback-mount')
