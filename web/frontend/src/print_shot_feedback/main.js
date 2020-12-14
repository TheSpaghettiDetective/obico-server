import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(VueSwal)

import App from './PrintShotFeedbackApp.vue'

new Vue({
  components: { App }
}).$mount('#print-shot-feedback-mount')
