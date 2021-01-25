import Vue from 'vue'
import VueSwal from 'common/VueSwal'
import setupSentry from '@lib/sentry'

setupSentry(Vue)
Vue.use(VueSwal)

import UserPreferencesPage from './UserPreferencesPage.vue'

new Vue({
  components: { UserPreferencesPage }
}).$mount('#user-preferences-mount')
