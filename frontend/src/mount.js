import Vue from 'vue'
import VueRouter from 'vue-router'
import VueSwal from '@src/lib/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'
import VueMoment from 'vue-moment'
import '@src/lib/filters'
import setupSentry from '@src/lib/sentry'
import { initTheme } from '@src/styles/colors'
import VuePluralize from 'vue-pluralize'

export default (router, components) => {
  initTheme()
  setupSentry(Vue)
  Vue.use(VueRouter)
  Vue.use(BootstrapVue)
  Vue.use(VueSwal)
  Vue.use(Sticky)
  Vue.use(VueMoment)
  Vue.use(VuePluralize)

  if (document.getElementById('app')) {
    new Vue({
      router,
      components,
    }).$mount('#app')
  }
}
