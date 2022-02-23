import VueRouter from 'vue-router'

import NewOctoPrintTunnelPage from '@src/views/NewOctoPrintTunnelPage.vue'
import OctoPrintTunnelPage from '@src/views/OctoPrintTunnelPage.vue'
import PrintShotFeedbackApp from '@src/views/PrintShotFeedbackApp.vue'
import PrintsPage from '@src/views/PrintsPage.vue'
import PrintPage from '@src/views/PrintPage.vue'
import UploadPrintPage from '@src/views/UploadPrintPage.vue'
import PrinterListPage from '@src/views/PrinterListPage.vue'
import SharedPrinterPage from '@src/views/SharedPrinterPage.vue'
import PrinterSettingsPage from '@src/views/PrinterSettingsPage.vue'
import PrinterWizardPage from '@src/views/PrinterWizardPage.vue'
import PrinterControlPage from '@src/views/PrinterControlPage.vue'
import GCodesPage from '@src/views/GCodesPage.vue'

// User preferences
import UserPreferencesPage from '@src/views/UserPreferencesPage.vue'
const router = new VueRouter({
  routes: [
    {
      path: '/',
      component: UserPreferencesPage,
    },
    {
      path: '/theme',
      component: UserPreferencesPage,
    },
    {
      path: '/profile',
      component: UserPreferencesPage,
    },
    {
      path: '/email',
      component: UserPreferencesPage,
    },
    {
      path: '/general_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/email_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/sms_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/pushbullet_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/discord_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/telegram_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/pushover_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/slack_notifications',
      component: UserPreferencesPage,
    },
    {
      path: '/authorized_apps',
      component: UserPreferencesPage,
    },
  ]
})

const components = {
  NewOctoPrintTunnelPage,
  OctoPrintTunnelPage,
  PrintShotFeedbackApp,
  PrinterListPage,
  SharedPrinterPage,
  PrinterSettingsPage,
  PrinterWizardPage,
  PrinterControlPage,
  GCodesPage,
  PrintsPage,
  PrintPage,
  UploadPrintPage,
  UserPreferencesPage,
}

export {
  router,
  components,
}
