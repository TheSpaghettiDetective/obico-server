import Vue from 'vue'
import VueRouter from 'vue-router'
import VueSwal from 'common/VueSwal'
import setupSentry from '@lib/sentry'
import { BootstrapVue } from 'bootstrap-vue'
import { initTheme } from '@main/themes'

initTheme()
setupSentry(Vue)
Vue.use(VueRouter)
Vue.use(VueSwal)
Vue.use(BootstrapVue)

import UserPreferencesRoute from './UserPreferencesRoute.vue'

const router = new VueRouter({
  routes: [
    {
      path: '/',
      component: UserPreferencesRoute,
    },
    {
      path: '/theme',
      component: UserPreferencesRoute,
    },
    {
      path: '/profile',
      component: UserPreferencesRoute,
    },
    {
      path: '/email',
      component: UserPreferencesRoute,
    },
    {
      path: '/notifications',
      component: UserPreferencesRoute,
    },
  ]
})

new Vue({
  router
}).$mount('#user-preferences-mount')
