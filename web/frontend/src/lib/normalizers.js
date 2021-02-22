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
  return {
    ...printer,
    createdAt: function() { return toMomentOrNull(this.created_at) },
    isOffline: function() { return get(this, 'status', null) === null },
    isPaused: function() { return get(this, 'status.state.flags.paused', false) },
    isIdle: function() { return get(this, 'status.state.text', '') === 'Operational' },
    isDisconnected: function() { return get(this, 'status.state.flags.closedOrError', true) },
    isPrinting: function() { return !this.isDisconnected() && get(this, 'status.state.text', '') !== 'Operational' },
    hasError: function() { return get(this, 'status.state.flags.error') || get(this, 'status.state.text', '').toLowerCase().includes('error') },
    alertUnacknowledged: function() {
        return get(this, 'current_print.alerted_at')
                && moment(
                    get(this, 'current_print.alerted_at')
                ).isAfter(
                    moment(get(this, 'current_print.alert_acknowledged_at') || 0)
                )
    },
  }
}


export const getNormalizedP = (predictions, currentPosition) => {
      const num = Math.round(predictions.length * currentPosition)
      return get(predictions[num], 'fields.normalized_p', 0)
}
