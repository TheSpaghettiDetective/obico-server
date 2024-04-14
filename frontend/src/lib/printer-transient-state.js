import Vue from 'vue'
import { isLocalStorageSupported } from '@static/js/utils'
import i18n from '@src/i18n/i18n.js'

const TRANSIENT_STATES = {
  'G-Code Downloading': {
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
  const timeOutInSeconds = printer.isAgentVersionGte('2.3.7', '1.4.2') ? 15 : 5 * 60
  const timeout = new Date(currentTime.getTime() + timeOutInSeconds * 1000)
  localStorage.setItem(`${prefix}-timeout`, timeout)
}

export const getPrinterCalculatedState = (printer, underlinedState) => {
  const printerId = printer.id

  if (!isLocalStorageSupported()) return underlinedState

  if (!underlinedState) {
    // Printer is offline or disconnected, clear transient state if any
    clearPrinterTransientState(printerId)
    return null
  }

  const prefix = `printer-${printerId}-state-transitioning`
  const persistedTransientState = localStorage.getItem(`${prefix}-name`)
  const timeout = localStorage.getItem(`${prefix}-timeout`)
  const fromStates = TRANSIENT_STATES[persistedTransientState]?.fromStates

  let calculatedState = underlinedState
  if (persistedTransientState && timeout && fromStates) {
    if (fromStates.includes(underlinedState)) {
      if (new Date() > new Date(timeout)) {
        clearPrinterTransientState(printerId)
        showTimeoutError(printer, persistedTransientState, underlinedState)
      } else {
        // underlinedState is still the previous state. Transition not finished
        calculatedState = persistedTransientState
      }
    } else {
      clearPrinterTransientState(printerId)
    }
  }

  return calculatedState
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
      title: `${i18n.t('Printer not responding')}`,
      html: `${i18n.t("The printer doesn't seem to be responding. Is it powered on and connected to the Internet? Please")} <a href="mailto:support@obico.io">${i18n.t("report the problem to us")}</a> ${i18n.t("if this error repeats multiple times.")}`,
    })
    .then(() => {
      window.location.reload()
    })
}
