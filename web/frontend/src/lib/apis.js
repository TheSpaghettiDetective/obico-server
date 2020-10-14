export default {
  printShotFeedback: (shotId, printId) => `/api/v1/printshotfeedbacks/${shotId}/?print_id=${printId}`,
  print: printId => `/api/v1/prints/${printId}/`,
  prints: () => '/api/v1/prints/',
  printsBulkDelete: () => '/api/v1/prints/bulk_delete/',
  printAlertOverwrite: printId => `/api/v1/prints/${printId}/alert_overwrite/`,
  printers: () => '/api/v1/printers/',
  printer: printerId => `/api/v1/printers/${printerId}/`,
  printerAction: (printerId, path) => `/api/v1/printers/${printerId}${path}`,
  pubPrinter: () => '/api/v1p/printer/',
  gcodes: () => '/api/v1/gcodes/',
  tunnelUsage: () => '/api/v1/tunnelusage/',
}
