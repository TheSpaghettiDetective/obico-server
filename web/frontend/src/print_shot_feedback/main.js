import Vue from 'vue'
import VueSwal from 'vue-swal'

Vue.use(VueSwal)

import App from './App.vue'

new Vue({
  components: {App}
}).$mount("#print-shot-feedback-mount")
