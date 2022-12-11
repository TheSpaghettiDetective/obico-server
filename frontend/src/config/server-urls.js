import entries from 'lodash/entries'
import map from 'lodash/map'

export default {
  // APIs
  printShotFeedback: (shotId, printId) => `/api/v1/printshotfeedbacks/${shotId}/?print_id=${printId}`,
  print: printId => `/api/v1/prints/${printId}/`,
  prints: () => '/api/v1/prints/',
  printsBulkDelete: () => '/api/v1/prints/bulk_delete/',
  printers: () => '/api/v1/printers/',
  printer: printerId => `/api/v1/printers/${printerId}/`,
  printerAction: (printerId, path) => `/api/v1/printers/${printerId}${path}`,
  pubPrinter: () => '/api/v1p/printer/',

  // Gcodes
  gcodeFile: (id) => `/api/v1/g_code_files/${id}/`,
  gcodeFiles: ({query, parentFolder, page, pageSize} = {}) => {
    const params = {
      // query: '' = all files; 'str' = filtered; null/undefined = don't include query param
      query: typeof query === 'string' ? 'q=' + query : '',
      // parentFolder: null = root; number = folderId; undefined = don't include parentFolder param
      parentFolder: (parentFolder || parentFolder === null) ? `parent_folder=${parentFolder}` : '',
      // pagination: if not provided, disable pagination
      page: `page=${page || 1}`,
      pageSize: `page_size=${pageSize || 9999}`,
    }
    let url = '/api/v1/g_code_files/?'
    for (const param of Object.values(params)) {
      url += param ? `${param}&` : ''
    }
    return url
  },
  gcodeFolder: (id) => `/api/v1/g_code_folders/${id}/`,
  gcodeFolders: ({page, pageSize, parentFolder} = {page: 1, pageSize: 9999, parentFolder: null}) =>
    `/api/v1/g_code_folders/?parent_folder=${parentFolder || null}&page=${page || 1}&page_size=${pageSize || 9999}`,

  gcode: gcodeId => `/api/v1/g_code_files/${gcodeId}/`,

  tunnels: () => '/api/v1/tunnels/',
  tunnel: (id) => `/api/v1/tunnels/${id}/`,
  tunnelUsage: () => '/api/v1/tunnelusage/',
  verificationCode: () => '/api/v1/onetimeverificationcodes/',
  user: () => '/api/v1/users/me/',
  sharedResources: (paramsObj) => '/api/v1/sharedresources/?'
    + map(entries(paramsObj), (entry) => entry.join('=')).join('&'),
  sharedResource: (resourceId) => `/api/v1/sharedresources/${resourceId}/`,
  printerDiscovery: () => '/api/v1/printer_discovery/',
  printerEvents: () => '/api/v1/printer_events/',

  // Notifications
  notificationPlugins: () => '/api/v1/notification_settings/available_plugins/',
  notificationChannels: () => '/api/v1/notification_settings/',
  updateNotificationChannel: (id) => `/api/v1/notification_settings/${id}/`,
  testNotificationChannel: (id) => `/api/v1/notification_settings/${id}/send_test_message/`,

  // App urls
  printerControl: printerId => `/printers/${printerId}/control/`,
  printerWebSocket: printerId => `/ws/web/${printerId}/`,
  printerSharedWebSocket: token => `/ws/share_token/web/${token}/`,
  printerWizard: printerId => `/printers/wizard/?printerId=${printerId}`
}
