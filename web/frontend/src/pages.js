import VueRouter from 'vue-router'
import routes from '@config/user-preferences/routes'
import wizardRoutes from '@src/views/printer-wizard/wizard-routes'

import NewOctoPrintTunnelPage from '@src/views/NewOctoPrintTunnelPage.vue'
import OctoPrintTunnelPage from '@src/views/OctoPrintTunnelPage.vue'
import PrintShotFeedbackApp from '@src/views/PrintShotFeedbackApp.vue'
import PrintsPage from '@src/views/PrintsPage.vue'
import PrintPage from '@src/views/PrintPage.vue'
import UploadPrintPage from '@src/views/UploadPrintPage.vue'
import PrinterListPage from '@src/views/PrinterListPage.vue'
import SharedPrinterPage from '@src/views/SharedPrinterPage.vue'
import PrinterSettingsPage from '@src/views/PrinterSettingsPage.vue'
import PrinterWizardPage from '@src/views/printer-wizard/PrinterWizardPage.vue'
import PrinterControlPage from '@src/views/PrinterControlPage.vue'
import GCodesPage from '@src/views/GCodesPage.vue'
import UserPreferencesPage from '@src/views/UserPreferencesPage.vue'

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/user_preferences',
      component: UserPreferencesPage,
    },
    ...Object.values(routes).map(route => ({
      path: route,
      component: UserPreferencesPage,
    })),

    ...Object.values(wizardRoutes).map(route => ({
      path: route,
      component: PrinterWizardPage,
    })),
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
