import entries from 'lodash/entries'
import map from 'lodash/map'

export default {
  // APIs
  printShotFeedback: (shotId, printId) =>
    `/api/v1/printshotfeedbacks/${shotId}/?print_id=${printId}`,
  print: (printId) => `/api/v1/prints/${printId}/`,
  prints: () => '/api/v1/prints/',
  printsBulkDelete: () => '/api/v1/prints/bulk_delete/',
  stats: () => `/api/v1/prints/stats/`,

  printers: () => '/api/v1/printers/',
  printer: (printerId) => `/api/v1/printers/${printerId}/`,
  printerAction: (printerId, path) => `/api/v1/printers/${printerId}${path}`,
  pubPrinter: () => '/api/v1p/printer/',

  tunnels: () => '/api/v1/tunnels/',
  tunnel: (id) => `/api/v1/tunnels/${id}/`,
  tunnelUsage: () => '/api/v1/tunnelusage/',
  verificationCode: () => '/api/v1/onetimeverificationcodes/',
  user: () => '/api/v1/users/me/',
  sharedResources: (paramsObj) =>
    '/api/v1/sharedresources/?' + map(entries(paramsObj), (entry) => entry.join('=')).join('&'),
  sharedResource: (resourceId) => `/api/v1/sharedresources/${resourceId}/`,
  printerDiscovery: () => '/api/v1/printer_discovery/',
  oneTimePasscodes: () => '/api/v1/one_time_passcodes/',

  printerEvents: () => '/api/v1/printer_events/',

  // Notifications
  notificationPlugins: () => '/api/v1/notification_settings/available_plugins/',
  notificationChannels: () => '/api/v1/notification_settings/',
  updateNotificationChannel: (id) => `/api/v1/notification_settings/${id}/`,
  testNotificationChannel: (id) => `/api/v1/notification_settings/${id}/send_test_message/`,

  // App urls
  printerControl: (printerId) => `/printers/${printerId}/control/`,
  printerWebSocket: (printerId) => `/ws/web/${printerId}/`,
  printerSharedWebSocket: (token) => `/ws/share_token/web/${token}/`,
  printerWizard: (printerId) => `/printers/wizard/?printerId=${printerId}`,

  // Gcodes
  gcodeFile: (id) => `/api/v1/g_code_files/${id}/`,
  gcodeFiles: () => '/api/v1/g_code_files/',
  gcodeFolder: (id) => `/api/v1/g_code_folders/${id}/`,
  gcodeFolders: () => '/api/v1/g_code_folders/',
  gcode: (gcodeId) => `/api/v1/g_code_files/${gcodeId}/`,
  gcodeFolderBulkDelete: () => '/api/v1/g_code_folders/bulk_delete/',
  gcodeFileBulkDelete: () => '/api/v1/g_code_files/bulk_delete/',
  gcodeFolderBulkMove: () => '/api/v1/g_code_folders/bulk_move/',
  gcodeFileBulkMove: () => '/api/v1/g_code_files/bulk_move/',

  // JusPrin
  jusprinMe: () => '/jusprin/api/me/',
  jusprinChats: (chatId) => (chatId ? `/jusprin/api/chats/${chatId}/` : `/jusprin/api/chats/`),
  jusprinChatMessages: (chat_id) => `/jusprin/api/chats/messages/`,
  jusprinPlateAnalysisProcess: () => '/jusprin/api/plate_analysis/',
  jusprinContactSupport: () => '/jusprin/api/contact_support/',
}
