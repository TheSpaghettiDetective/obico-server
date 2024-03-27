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
import moment from 'moment'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faStar,
  faFileCode,
  faCalendarDays,
  faChartPie,
  faMoneyCheckDollar,
  faCircleQuestion,
  faBell,
  faCog,
  faCirclePause,
  faCirclePlay,
  faCircleXmark,
  faPowerOff,
  faGear,
  faRotateRight,
  faLayerGroup,
  faChevronDown,
  faRulerVertical,
} from '@fortawesome/free-solid-svg-icons'
import { faDiscord } from '@fortawesome/free-brands-svg-icons'

const urlParams = new URLSearchParams(window.location.search)
Vue.prototype.$brand = urlParams.get('theme')

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
      errorDialog: function (errorObj, userMessage) {
        console.error('logError', errorObj)
        if (userMessage) {
          this.$swal.Reject.fire({
            title: 'Error',
            html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
              ${userMessage}.
              Get help from <a href="https://obico.io/discord-obico-klipper">Obico for Klipper support forum</a> or <a href="https://obico.io/discord">the Obico general support forum</a> if this error persists.
            </p>`,
            showConfirmButton: false,
            showCancelButton: true,
            cancelButtonText: 'Close',
          })
        }
      },
    },
  })

  Vue.component('LoadingPlaceholder', LoadingPlaceholder)

  library.add(
    faStar,
    faFileCode,
    faCalendarDays,
    faChartPie,
    faMoneyCheckDollar,
    faCircleQuestion,
    faBell,
    faCog,
    faDiscord,
    faRotateRight,
    faCirclePause,
    faCirclePlay,
    faCircleXmark,
    faPowerOff,
    faGear,
    faLayerGroup,
    faChevronDown,
    faRulerVertical
  )
  Vue.component('FontAwesomeIcon', FontAwesomeIcon)

  if (document.getElementById('app')) {
    new Vue({
      router,
      components,
    }).$mount('#app')
  }

  // FIXME: make start of the week dynamic when/if it will be done in the backend
  moment.updateLocale('en', {
    week: {
      dow: 0, // Sunday is the first day of the week.
    },
  })
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js').catch(err => {
      console.error('ServiceWorker registration failed: ', err);
    });
  });
}