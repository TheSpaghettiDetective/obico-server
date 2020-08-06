import get from 'lodash/get'
import moment from 'moment'


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


let shouldShowAlert = (printer) => {
  if (!printer.current_print || !printer.current_print.alerted_at) {
    return false
  }
  return moment(
    printer.current_print.alerted_at
  ).isAfter(
    moment(printer.current_print.alert_acknowledged_at || 0)
  )
}


let getLocalPref = (prefId, defaultValue) => {
  var val = localStorage.getItem(prefId) || defaultValue
  // Hack to deal with data type such as boolean and number
  try {
    return JSON.parse(val)
  } catch (e) {
    return val
  }
}

let setLocalPref = (prefId, value) => {
  return localStorage.setItem(prefId, value)
}

let getPrinterLocalPref = (prefix, printerId, defaultValue) => {
  var itemId = prefix + String(printerId)
  var val = localStorage.getItem(itemId) || defaultValue
  try {
    return JSON.parse(val)
  } catch (e) {
    return val
  }
}

let setPrinterLocalPref = (prefix, printerId, value) => {
  var itemId = prefix + String(printerId)
  return localStorage.setItem(itemId, value)
}

let toDuration = (seconds, printerState) => {
  if (seconds == null || seconds == 0) {
    return {
      valid: false,
      printing: printInProgress(printerState),
    }
  } else {
    var d = moment.duration(seconds, 'seconds')
    var h = Math.floor(d.asHours())
    var m = d.minutes()
    var s = d.seconds()
    return {
      valid: true,
      printing: true,
      hours: h,
      showHours: (h>0),
      minutes: m,
      showMinutes: (h>0 || m>0),
      seconds: s,
      showSeconds: (h==0 && m==0)
    }
  }
}

export {
  isPrinterIdle,
  isPrinterPaused,
  isPrinterDisconnected,
  printerHasError,
  printInProgress,
  shouldShowAlert,
  getLocalPref,
  setLocalPref,
  getPrinterLocalPref,
  setPrinterLocalPref,
  toDuration,
}
