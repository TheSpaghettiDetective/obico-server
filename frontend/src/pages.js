import VueRouter from 'vue-router'
import prefRoutes from '@config/user-preferences/pref-routes'

import NewOctoPrintTunnelPage from '@src/views/NewOctoPrintTunnelPage.vue'
import OctoPrintTunnelPage from '@src/views/OctoPrintTunnelPage.vue'
import PrintShotFeedbackApp from '@src/views/PrintShotFeedbackApp.vue'
import PrintHistoryPage from '@src/views/PrintHistoryPage.vue'
import StatsPage from '@src/views/StatsPage.vue'
import PrintsPage from '@src/views/PrintsPage.vue'
import PrintPage from '@src/views/PrintPage.vue'
import UploadPrintPage from '@src/views/UploadPrintPage.vue'
import PrinterListPage from '@src/views/PrinterListPage.vue'
import SharedPrinterPage from '@src/views/SharedPrinterPage.vue'
import PrinterSettingsPage from '@src/views/PrinterSettingsPage.vue'
import PrinterLinkingPage from '@src/views/printer-wizard/PrinterLinkingPage.vue'
import TargetPlatformSelectionPage from '@src/views/printer-wizard/TargetPlatformSelectionPage.vue'
import ObicoInstallationGuidePage from '@src/views/printer-wizard/ObicoInstallationGuidePage.vue'
import AddPrinterSuccessPage from '@src/views/printer-wizard/AddPrinterSuccessPage.vue'
import PrinterControlPage from '@src/views/PrinterControlPage.vue'
import GCodeFoldersPage from '@src/views/GCodeFoldersPage.vue'
import GCodeFilePage from '@src/views/GCodeFilePage.vue'
import UserPreferencesPage from '@src/views/UserPreferencesPage.vue'
import PrinterEventsPage from '@src/views/PrinterEventsPage.vue'
import PrinterTerminalPage from '@src/views/PrinterTerminalPage.vue'
import FirstLayerInspectionImagePage from '@src/views/FirstLayerInspectionImagePage.vue'
import { EmbeddedChatV10Page, EmbeddedChatV12Page } from '@src/views/jusprin'


  const routes = [
    {
      path: '/g_code_folders/cloud/:parentFolder/',
      component: GCodeFoldersPage,
    },
    {
      path: '/g_code_folders/local/:printerId/:parentFolder?/',
      component: GCodeFoldersPage,
    },
    {
      path: '/g_code_files/cloud/:fileId/',
      component: GCodeFilePage,
    },
    {
      path: '/g_code_files/local/:printerId/:fileId/',
      component: GCodeFilePage,
    },
    {
      path: '/user_preferences/',
      component: UserPreferencesPage,
    },
    {
      path: '/printers/wizard/',
      component: TargetPlatformSelectionPage,
    },
    {
      path: '/printers/wizard/guide/:targetPlatform/',
      component: ObicoInstallationGuidePage,
    },
    {
      path: '/printers/wizard/link/:targetPlatform/',
      component: PrinterLinkingPage,
    },
    {
      path: '/printers/wizard/success/:printerId/',
      component: AddPrinterSuccessPage,
    },
    ...Object.values(prefRoutes).map((route) => ({
      path: route,
      component: UserPreferencesPage,
    })),
  ]

const components = {
  NewOctoPrintTunnelPage,
  OctoPrintTunnelPage,
  PrintShotFeedbackApp,
  PrinterListPage,
  SharedPrinterPage,
  PrinterSettingsPage,
  PrinterLinkingPage,
  PrinterControlPage,
  GCodeFoldersPage,
  GCodeFilePage,
  PrintsPage,
  PrintPage,
  PrintHistoryPage,
  StatsPage,
  UploadPrintPage,
  UserPreferencesPage,
  PrinterEventsPage,
  PrinterTerminalPage,
  FirstLayerInspectionImagePage,
  EmbeddedChatV10Page,
  EmbeddedChatV12Page,
}

export { routes, components }
