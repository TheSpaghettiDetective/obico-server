import moment from 'moment'

/***** Other helpers */

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

let toDuration = (seconds, isPrinting) => {
  if (seconds == null || seconds == 0) {
    return {
      valid: false,
      printing: isPrinting,
    }
  } else {
    var d = moment.duration(seconds, 'seconds')
    var h = Math.floor(d.asHours())
    var m = d.minutes()
    var s = d.seconds()
    return {
      valid: true,
      printing: isPrinting,
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
  shouldShowAlert,
  getLocalPref,
  setLocalPref,
  getPrinterLocalPref,
  setPrinterLocalPref,
  toDuration,
}
