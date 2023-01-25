import VueRouter from 'vue-router'
import routes from '@config/user-preferences/routes'
import wizardRoutes from '@src/views/printer-wizard/wizard-routes'

import NewOctoPrintTunnelPage from '@src/views/NewOctoPrintTunnelPage.vue'
import OctoPrintTunnelPage from '@src/views/OctoPrintTunnelPage.vue'
import PrintShotFeedbackApp from '@src/views/PrintShotFeedbackApp.vue'
import PrintHistoryPage from '@src/views/PrintHistoryPage.vue'
import PrintsPage from '@src/views/PrintsPage.vue'
import PrintPage from '@src/views/PrintPage.vue'
import UploadPrintPage from '@src/views/UploadPrintPage.vue'
import PrinterListPage from '@src/views/PrinterListPage.vue'
import SharedPrinterPage from '@src/views/SharedPrinterPage.vue'
import PrinterSettingsPage from '@src/views/PrinterSettingsPage.vue'
import PrinterWizardPage from '@src/views/printer-wizard/PrinterWizardPage.vue'
import PrinterControlPage from '@src/views/PrinterControlPage.vue'
import GCodeFoldersPage from '@src/views/GCodeFoldersPage.vue'
import GCodeFilePage from '@src/views/GCodeFilePage.vue'
import UserPreferencesPage from '@src/views/UserPreferencesPage.vue'
import PrinterEventsPage from '@src/views/PrinterEventsPage.vue'

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/g_code_folders/cloud/:parentFolder',
      component: GCodeFoldersPage,
    },
    {
      path: '/g_code_folders/local/:printerId/:parentFolder?',
      component: GCodeFoldersPage,
    },
    {
      path: '/g_code_files/cloud/:fileId',
      component: GCodeFilePage,
    },
    {
      path: '/g_code_files/local/:printerId/:fileId',
      component: GCodeFilePage,
    },
    {
      path: '/user_preferences',
      component: UserPreferencesPage,
    },
    ...Object.values(routes).map((route) => ({
      path: route,
      component: UserPreferencesPage,
    })),

    ...Object.values(wizardRoutes).map((route) => ({
      path: route,
      component: PrinterWizardPage,
    })),
  ],
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
  GCodeFoldersPage,
  GCodeFilePage,
  PrintsPage,
  PrintPage,
  PrintHistoryPage,
  UploadPrintPage,
  UserPreferencesPage,
  PrinterEventsPage,
}

export { router, components }
