import Vue from 'vue'
import VueRouter from 'vue-router'
import VueSwal from '@src/lib/VueSwal'
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'
import VueMoment from 'vue-moment'
import '@src/lib/filters'
import setupSentry from '@src/lib/sentry'
import { initTheme } from '@src/lib/color-scheme-controller'
import VuePluralize from 'vue-pluralize'
import OnoffToggle from 'vue-onoff-toggle'

export default (router, components) => {
  initTheme()
  setupSentry(Vue)
  Vue.use(VueRouter)
  Vue.use(BootstrapVue)
  Vue.use(VueSwal)
  Vue.use(Sticky)
  Vue.use(VueMoment)
  Vue.use(VuePluralize)
  Vue.use(OnoffToggle)

  if (document.getElementById('app')) {
    new Vue({
      router,
      components,
    }).$mount('#app')
  }
}
