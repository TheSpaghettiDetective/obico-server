import Vue from 'vue'
import VueSwal from 'vue-sweetalert2'
import VueContentPlaceholders from "vue-content-placeholders"

Vue.use(VueSwal)
Vue.use(VueContentPlaceholders);

import App from './App.vue'

new Vue({
    components: { App }
}).$mount("#print-shot-feedback-mount")
