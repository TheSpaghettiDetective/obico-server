import { getLocalPref, setLocalPref } from '@src/lib/pref'

export const setTransientState = (printerId, transientState) => {
  let fromStates = []

  switch (transientState) {
    case 'Connecting':
      fromStates = ['Offline']
      break
    case 'Starting':
      fromStates = ['Operational', 'Starting']
      break
    case 'Pausing':
      fromStates = ['Printing', 'Pausing']
      break
    case 'Resuming':
      fromStates = ['Paused', 'Resuming']
      break
    case 'Cancelling':
      // cancelling could be from paused or printing
      fromStates = ['Printing', 'Paused', 'Cancelling']
      break
    default:
      console.error('Unknown transient state: ' + transientState)
      break
  }

  setLocalPref('printer-' + printerId + '-state-transitioning-from', JSON.stringify(fromStates))
  setLocalPref('printer-' + printerId + '-state-transitioning-name', transientState)

  const timeout = new Date()
  timeout.setMinutes(timeout.getMinutes() + 5)
  setLocalPref('printer-' + printerId + '-state-transitioning-timeout', timeout)
}

export const getTransientState = (printerId, currentState) => {
  const fromStates = getLocalPref('printer-' + printerId + '-state-transitioning-from')
  const transientStateName = getLocalPref('printer-' + printerId + '-state-transitioning-name')
  const timeout = getLocalPref('printer-' + printerId + '-state-transitioning-timeout')

  if (!fromStates || !transientStateName || !timeout) {
    return null
  }

  if (currentState && !fromStates.includes(currentState)) {
    setLocalPref('printer-' + printerId + '-state-transitioning-from', null)
    setLocalPref('printer-' + printerId + '-state-transitioning-name', null)
    setLocalPref('printer-' + printerId + '-state-transitioning-timeout', null)
    return null
  }

  if (new Date() > new Date(timeout)) {
    setLocalPref('printer-' + printerId + '-state-transitioning-from', null)
    setLocalPref('printer-' + printerId + '-state-transitioning-name', null)
    setLocalPref('printer-' + printerId + '-state-transitioning-timeout', null)
    return 'timeout'
  }

  return { fromStates, transientStateName, timeout: new Date(timeout) }
}
