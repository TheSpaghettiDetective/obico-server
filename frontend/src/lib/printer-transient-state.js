import { isLocalStorageSupported } from '@static/js/utils'

export const setTransientState = (printerId, transientState) => {
  if (!isLocalStorageSupported()) return
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

  localStorage.setItem(
    'printer-' + printerId + '-state-transitioning-from',
    JSON.stringify(fromStates)
  )
  localStorage.setItem('printer-' + printerId + '-state-transitioning-name', transientState)

  const timeout = new Date()
  timeout.setMinutes(timeout.getMinutes() + 5)
  localStorage.setItem('printer-' + printerId + '-state-transitioning-timeout', timeout)
}

export const getTransientState = (printerId, currentState) => {
  if (!isLocalStorageSupported()) return

  let fromStates = JSON.parse(
    localStorage.getItem('printer-' + printerId + '-state-transitioning-from')
  )
  const transientStateName = localStorage.getItem(
    'printer-' + printerId + '-state-transitioning-name'
  )
  const timeout = localStorage.getItem('printer-' + printerId + '-state-transitioning-timeout')

  if (!fromStates || !transientStateName || !timeout) {
    return null
  }

  if (currentState && !fromStates.includes(currentState)) {
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-from')
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-name')
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-timeout')
    return null
  }

  if (new Date() > new Date(timeout)) {
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-from')
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-name')
    localStorage.removeItem('printer-' + printerId + '-state-transitioning-timeout')
    return 'timeout'
  }

  return { fromStates, transientStateName, timeout: new Date(timeout) }
}
