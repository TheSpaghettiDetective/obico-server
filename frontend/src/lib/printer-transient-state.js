import Vue from 'vue'
import { isLocalStorageSupported } from '@static/js/utils'

const TRANSIENT_STATES = {
  'Downloading G-Code': {
    fromStates: ['Operational'],
  },
  Starting: {
    fromStates: ['Operational'],
  },
  Pausing: {
    fromStates: ['Printing'],
  },
  Resuming: {
    fromStates: ['Paused'],
  },
  Cancelling: {
    fromStates: ['Printing', 'Paused'],
  },
}

export const setPrinterTransientState = (printer, transientStateName) => {
  const printerId = printer.id
  if (!isLocalStorageSupported()) return
  const prefix = `printer-${printerId}-state-transitioning`
  localStorage.setItem(`${prefix}-name`, transientStateName)

  const currentTime = new Date()
  // Agents in older versions didn't have all transient states implemented. So we make it more forgiving even if it increases the chance for app to be stuck in a transient state.
  const timeOutInSeconds = printer.isAgentVersionGte('2.3.7', '1.3.7') ? 10 : 5 * 60
  const timeout = new Date(currentTime.getTime() + timeOutInSeconds * 1000)
  localStorage.setItem(`${prefix}-timeout`, timeout)
}

export const getPrinterTransientState = (printer, underlinedState, timeoutCallback) => {
  const printerId = printer.id

  if (!isLocalStorageSupported()) return

  if (!underlinedState) {
    // Printer is offline or disconnected, clear transient state if any
    clearPrinterTransientState(printerId)
    return null
  }

  const prefix = `printer-${printerId}-state-transitioning`
  const persistedTransientState = localStorage.getItem(`${prefix}-name`)
  const timeout = localStorage.getItem(`${prefix}-timeout`)
  const fromStates = TRANSIENT_STATES[persistedTransientState]?.fromStates

  if (!persistedTransientState || !timeout || !fromStates) {
    // No persistedTransientState. Return underlinedState if it is a transient state
    return underlinedState in TRANSIENT_STATES ? underlinedState : null
  }

  if (new Date() > new Date(timeout)) {
    clearPrinterTransientState(printerId)
    showTimeoutError(printer, persistedTransientState, underlinedState)
    return null
  }

  if (fromStates.includes(underlinedState)) {
    // underlinedState is still the previous state. Transition not finished
    return persistedTransientState
  } else {
    clearPrinterTransientState(printerId)
    return underlinedState in TRANSIENT_STATES ? underlinedState : null
  }
}

export const clearPrinterTransientState = (printerId) => {
  if (!isLocalStorageSupported()) return
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
