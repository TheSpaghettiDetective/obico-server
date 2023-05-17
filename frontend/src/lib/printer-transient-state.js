import { isLocalStorageSupported } from '@static/js/utils'
import isEqual from 'lodash/isEqual'

const TRANSIENT_STATES = {
  Connecting: {
    fromStates: ['Offline'],
    title: 'Connecting',
    timeoutSeconds: 10,
  },
  Starting: {
    fromStates: ['Operational', 'Starting'],
    title: 'Starting',
    timeoutSeconds: 10,
  },
  'Downloading G-Code': {
    fromStates: ['Downloading G-Code'],
    title: 'Downloading G-Code',
    timeoutSeconds: 10 * 60,
  },
  Pausing: {
    fromStates: ['Printing', 'Pausing'],
    title: 'Pausing',
    timeoutSeconds: 2 * 60,
  },
  Resuming: {
    fromStates: ['Paused', 'Resuming'],
    title: 'Resuming',
    timeoutSeconds: 5 * 60,
  },
  Cancelling: {
    fromStates: ['Printing', 'Paused', 'Cancelling'],
    title: 'Cancelling',
    timeoutSeconds: 2 * 60,
  },
}

export const setTransientState = (printerId, transientStateName) => {
  if (!isLocalStorageSupported()) return
  const transientState = TRANSIENT_STATES[transientStateName]
  const prefix = `printer-${printerId}-state-transitioning`

  localStorage.setItem(`${prefix}-from`, JSON.stringify(transientState.fromStates))
  localStorage.setItem(`${prefix}-name`, transientStateName)

  const timeout = new Date()
  timeout.setSeconds(timeout.getSeconds() + transientState.timeoutSeconds)
  localStorage.setItem(`${prefix}-timeout`, timeout)
}

export const getTransientState = (printerId, currentState) => {
  if (!isLocalStorageSupported()) return

  if (!currentState) {
    // Printer is offline or disconnected, clear transient state if any
    clearTransientState(printerId)
    return null
  }

  const prefix = `printer-${printerId}-state-transitioning`
  let fromStates = JSON.parse(localStorage.getItem(`${prefix}-from`))
  const transientStateName = localStorage.getItem(`${prefix}-name`)
  const timeout = localStorage.getItem(`${prefix}-timeout`)

  if (!fromStates || !transientStateName || !timeout) {
    // No transient state in storage
    return null
  }

  if (!fromStates.includes(currentState)) {
    // Printer is moved to the next state, clear transient state

    // Special case: if printer is in 'GCodeDownloading' state, move it there
    if (currentState === 'Downloading G-Code' && isEqual(fromStates, ['Operational', 'Starting'])) {
      setTransientState(printerId, 'Downloading G-Code')
      return getTransientState(printerId, currentState)
    }

    clearTransientState(printerId)
    return null
  }

  if (new Date() > new Date(timeout)) {
    // Transient state has timed out, clear it
    clearTransientState(printerId)
    return 'timeout'
  }

  return {
    ...TRANSIENT_STATES[transientStateName],
    name: transientStateName,
    timeout: new Date(timeout),
  }
}

export const clearTransientState = (printerId) => {
  if (!isLocalStorageSupported()) return
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-from')
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-name')
  localStorage.removeItem('printer-' + printerId + '-state-transitioning-timeout')
}
