import VueRouter from 'vue-router'

// common
import SvgSprite from '@src/common/SvgSprite.vue'

// octoprint_tunnel
import NewOctoPrintTunnelPage from '@src/octoprint_tunnel/NewOctoPrintTunnelPage.vue'
import OctoPrintTunnelPage from '@src/octoprint_tunnel/OctoPrintTunnelPage.vue'

// print_shot_feedback
import PrintShotFeedbackApp from '@src/print_shot_feedback/PrintShotFeedbackApp.vue'

// printers
import PrinterListPage from '@src/printers/PrinterListPage.vue'
import SharedPrinterPage from '@src/printers/SharedPrinterPage.vue'
import PrinterSettingsPage from '@src/printers/PrinterSettingsPage.vue'
import PrinterWizardPage from '@src/printers/PrinterWizardPage.vue'
import PrinterControlPage from '@src/printers/PrinterControlPage.vue'
import SharePrinter from '@src/printers/SharePrinter.vue'
import GCodesPage from '@src/printers/GCodesPage.vue'

// prints
import PrintsPage from '@src/prints/PrintsPage.vue'
import PrintPage from '@src/prints/PrintPage.vue'
import UploadPrintPage from '@src/prints/UploadPrintPage.vue'

// user
import UserPreferencesRoute from '@src/users/UserPreferencesRoute.vue'
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
      path: '/general_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/email_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/sms_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/pushbullet_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/discord_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/telegram_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/pushover_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/slack_notifications',
      component: UserPreferencesRoute,
    },
    {
      path: '/authorized_apps',
      component: UserPreferencesRoute,
    },
  ]
})

const components = {
  SvgSprite,
  NewOctoPrintTunnelPage,
  OctoPrintTunnelPage,
  PrintShotFeedbackApp,
  PrinterListPage,
  SharedPrinterPage,
  PrinterSettingsPage,
  PrinterWizardPage,
  PrinterControlPage,
  SharePrinter,
  GCodesPage,
  PrintsPage,
  PrintPage,
  UploadPrintPage,
  UserPreferencesRoute,
}

export {
  router,
  components,
}
