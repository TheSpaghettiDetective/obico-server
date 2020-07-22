import get from 'lodash/get'


let isPrinterIdle = (printerState) =>
  get(printerState, 'text', '') === 'Operational'

let isPrinterPaused = (printerState) =>
  get(printerState, 'flags.paused', false)

let isPrinterDisconnected = (printerState) =>
  get(printerState, 'flags.closedOrError', true)

let printerHasError = (printerState) => 
  get(printerState, 'flags.error') ||
  get(printerState, 'text', '').toLowerCase().includes('error')

let printInProgress = (printerState) =>
  !isPrinterDisconnected(printerState) &&
  get(printerState, 'text', '') !== 'Operational'

export {
  isPrinterIdle,
  isPrinterPaused,
  isPrinterDisconnected,
  printerHasError,
  printInProgress
}
