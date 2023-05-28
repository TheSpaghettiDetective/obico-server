import Vue from 'vue'
import { isLocalStorageSupported } from '@static/js/utils'

const TRANSIENT_STATES = {
  'Downloading G-Code': {
    fromStates: ['Operational'],
    title: 'Downloading G-Code',
    timeoutSeconds: 10 * 60,
  },
  Starting: {
    fromStates: ['Operational', 'Downloading G-Code'],
    title: 'Starting',
    timeoutSeconds: 10,
  },
  Pausing: {
    fromStates: ['Printing'],
    title: 'Pausing',
    timeoutSeconds: 2 * 60,
  },
  Resuming: {
    fromStates: ['Paused'],
    title: 'Resuming',
    timeoutSeconds: 5 * 60,
  },
  Cancelling: {
    fromStates: ['Printing', 'Paused'],
    title: 'Cancelling',
    timeoutSeconds: 2 * 60,
  },
}

export const setPrinterTransientState = (printer, transientStateName) => {
  const printerId = printer.id
  if (!isLocalStorageSupported()) return
  const transientState = TRANSIENT_STATES[transientStateName]
  const prefix = `printer-${printerId}-state-transitioning`

  localStorage.setItem(`${prefix}-from`, JSON.stringify(transientState.fromStates))
  localStorage.setItem(`${prefix}-name`, transientStateName)

  const timeout = new Date()
  timeout.setSeconds(timeout.getSeconds() + transientState.timeoutSeconds)
  localStorage.setItem(`${prefix}-timeout`, timeout)
}

export const getPrinterTransientState = (printer, nextState) => {
  const printerId = printer.id

  if (!isLocalStorageSupported()) return

  if (!nextState) {
    // Printer is offline or disconnected, clear transient state if any
    clearPrinterTransientState(printerId)
    return
  }

  const prefix = `printer-${printerId}-state-transitioning`
  let fromStates = JSON.parse(localStorage.getItem(`${prefix}-from`))
  const transientStateName = localStorage.getItem(`${prefix}-name`)
  const timeout = localStorage.getItem(`${prefix}-timeout`)

  if (!fromStates || !transientStateName || !timeout) {
    // No transient state in storage
    return
  }

  if (!fromStates.includes(nextState)) {
    if (nextState === transientStateName) {
      // Printer is still in the transient state, return it
      return {
        ...TRANSIENT_STATES[transientStateName],
        name: transientStateName,
        timeout: new Date(timeout),
      }
    } else if (transientStateName === 'Downloading G-Code' && nextState === 'Starting') {
      // Special case for OctoPrint (move from Downloading to Starting)
      setPrinterTransientState(printerId, 'Starting')
      return getPrinterTransientState(printer, nextState)
    } else {
      clearPrinterTransientState(printerId)
      return
    }
  }

  if (new Date() > new Date(timeout)) {
    // Transient state has timed out, clear it
    return {
      overTimeout: true,
      ...TRANSIENT_STATES[transientStateName],
      name: transientStateName,
      timeout: new Date(timeout),
    }
  }

  return {
    ...TRANSIENT_STATES[transientStateName],
    name: transientStateName,
    timeout: new Date(timeout),
  }
}

export const clearPrinterTransientState = (printerId) => {
  if (!isLocalStorageSupported()) return
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-from')
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-name')
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-timeout')
}

export const showTimeoutError = (printer, localTransientState, newPrinterState) => {
  window.Sentry?.captureMessage(
    `Transient state timeout: "${localTransientState}" -> "${newPrinterState}" (printer ID: ${printer.id})`
  )

  Vue.swal
    .fire({
      icon: 'error',
      title: 'Timeout Error',
      html: `Haven't received "${
        printer.name
      }" state update within proper timeframe. You can restart your ${printer.agentDisplayName()} and try again.<br><br>Get help from <a href="https://obico.io/discord">the Obico app discussion forum</a> if this error persists.</div>`,
    })
    .then(() => {
      window.location.reload()
    })
}
