
import { isLocalStorageSupported } from '@static/js/utils'

export const getLocalPref = (prefId, defaultValue) => {
  var savedVal = isLocalStorageSupported() ? localStorage.getItem(prefId) : null
  var val = savedVal || defaultValue
  // Hack to deal with data type such as boolean and number
  try {
    return JSON.parse(val)
  } catch (e) {
    return val
  }
}

export const setLocalPref = (prefId, value) => {
  if (isLocalStorageSupported()) {
    localStorage.setItem(prefId, value)
  }
}
