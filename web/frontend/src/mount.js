import Vue from 'vue'
import VueRouter from 'vue-router'
import VueSwal from '@common/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'
import VueMoment from 'vue-moment'
import '@common/filters'
import setupSentry from '@lib/sentry'
import { initTheme } from '@main/colors'
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

  if (document.getElementById('vue_app')) {
    new Vue({
      router,
      components,
    }).$mount('#vue_app')
  }
}
