import moment from 'moment'
import get from 'lodash/get'

export const toMomentOrNull = datetimeStr => {
  if (!datetimeStr) {
    return null
  }
  return moment(datetimeStr)
}

export const normalizedPrint = print => {
  print.ended_at = toMomentOrNull(print.cancelled_at || print.finished_at)
  print.started_at = toMomentOrNull(print.started_at)
  print.uploaded_at = toMomentOrNull(print.uploaded_at)
  print.has_alerts = Boolean(print.alerted_at)
  return print
}

export const normalizedPrinter = printer => {
  printer.name = printer.name || ('Printer #' + printer.id.toString())
  printer.created_at = toMomentOrNull(printer.created_at)
  printer.isPaused = get(printer, 'status.state.flags.paused', false)
  printer.isIdle = get(printer, 'status.state.text', '') === 'Operational'
  printer.isDisconnected = get(printer, 'status.state.flags.closedOrError', true)
  printer.isPrinting = !printer.isDisconnected && get(printer, 'status.state.text', '') !== 'Operational'
  printer.hasError = get(printer, 'status.state.flags.error') || get(printer, 'status.state.text', '').toLowerCase().includes('error')

  return printer
}
