import Vue from 'vue'
import VueSwal from 'common/VueSwal'

Vue.use(VueSwal)

import App from './PrintShotFeedbackApp.vue'

new Vue({
  components: { App }
}).$mount('#print-shot-feedback-mount')
