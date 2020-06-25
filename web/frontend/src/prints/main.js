import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import VueContentPlaceholders from "vue-content-placeholders";
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'

Vue.use(BootstrapVue)
Vue.use(VueSwal)
Vue.use(VueContentPlaceholders);
Vue.use(Sticky)

import App from './PrintsApp.vue'

new Vue({
    components: { App }
}).$mount("#prints-mount")
