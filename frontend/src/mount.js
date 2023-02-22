import Vue from 'vue'
import VueRouter from 'vue-router'
import VueSwal from '@src/lib/vue-swal'
import { BootstrapVue } from 'bootstrap-vue'
import Sticky from 'vue-sticky-directive'
import VueMoment from 'vue-moment'
import '@src/lib/filters'
import setupSentry from '@src/lib/sentry'
import { initTheme } from '@src/lib/color-scheme-controller'
import VuePluralize from 'vue-pluralize'
import OnoffToggle from 'vue-onoff-toggle'
import LoadScript from 'vue-plugin-load-script'
import LoadingPlaceholder from '@src/components/LoadingPlaceholder.vue'

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
  Vue.use(LoadScript)

  Vue.mixin({
    methods: {
      _showErrorPopup: function (error, userMessage) {
        console.error(error)
        this.$swal.Reject.fire({
          title: 'Error',
          html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
            ${userMessage || error?.message || 'Error occured'}.
            Get help from <a href="https://obico.io/discord">the Obico app discussion forum</a> if this error persists.
          </p>`,
          showConfirmButton: false,
          showCancelButton: true,
          cancelButtonText: 'Close',
        })
      },
    },
  })

  Vue.component('LoadingPlaceholder', LoadingPlaceholder)

  if (document.getElementById('app')) {
    new Vue({
      router,
      components,
    }).$mount('#app')
  }
}
