import { isLocalStorageSupported } from '@static/js/utils'

export const getLocalPref = (prefId, defaultValue, printerId = null) => {
  const storageKey = printerId === null ? prefId : `${prefId}_${printerId}`;
  var savedVal = isLocalStorageSupported() ? localStorage.getItem(storageKey) : null
  var val = savedVal || defaultValue
  // Hack to deal with data type such as boolean and number
  try {
    return JSON.parse(val)
  } catch (e) {
    return val
  }
}

export const setLocalPref = (prefId, value, printerId = null) => {
  if (isLocalStorageSupported()) {
    const storageKey = printerId === null ? prefId : `${prefId}_${printerId}`;
    localStorage.setItem(storageKey, value);
  }
}