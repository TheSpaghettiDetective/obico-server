import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import VueContentPlaceholders from "vue-content-placeholders"

Vue.use(VueSwal)
Vue.use(VueContentPlaceholders);

import App from './PrintShotFeedbackApp.vue'

new Vue({
    components: { App }
}).$mount("#print-shot-feedback-mount")
