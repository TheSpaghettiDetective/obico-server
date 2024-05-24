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
import SyndicateAwareSVG from '@src/components/SyndicateAwareSVG.vue'
import moment from 'moment'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import i18next from "@src/i18n/i18n.js";
import I18NextVue from "i18next-vue";
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
  faCheck
} from '@fortawesome/free-solid-svg-icons'
import { faDiscord } from '@fortawesome/free-brands-svg-icons'
import { syndicate, language } from '@src/lib/page-context'
import { syndicateTextConstant } from '@src/config/syndicateText'

Vue.prototype.$syndicate = syndicate().name
Vue.prototype.$syndicateText = syndicateTextConstant[syndicate().name||'base'] || syndicateTextConstant.base

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
  Vue.use(I18NextVue, { i18next });
  Vue.mixin({
    methods: {
      errorDialog: function (errorObj, userMessage) {
        console.error('logError', errorObj)
        if (userMessage) {
          this.$swal.Reject.fire({
            title: `${this.$i18next.t('Error')}`,
            html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
              ${userMessage}.
              ${this.$i18next.t("Get help from")} <a href="https://obico.io/discord-obico-klipper">${this.$i18next.t("the {brandName} for Klipper support forum",{brandName:this.$syndicateText.brandName})}</a> ${this.$i18next.t("or")} <a href="https://obico.io/discord">${this.$i18next.t('the {brandName} general support forum',{brandName:this.$syndicateText.brandName})}</a> ${this.$i18next.t("if this error persists.")}
            </p>`,
            showConfirmButton: false,
            showCancelButton: true,
            cancelButtonText: 'Close',
          })
        }
      },
      getDocRoot(path) {
        return this.$syndicateText.docRoot + path;
      },
      getAppRoot(path) {
        if(path)
          return this.$syndicateText.appRoot + path;
        else
        return this.$syndicateText.appRoot;
      }
    },
  })

  Vue.component('LoadingPlaceholder', LoadingPlaceholder)
  Vue.component('SyndicateAwareSVG', SyndicateAwareSVG)

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
    faRulerVertical,
    faCheck
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
