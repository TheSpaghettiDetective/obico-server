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

export const setLocalPref = (prefId, value, printerId = null) => {
  if (isLocalStorageSupported()) {
    if(printerId)
      {
    const storageKey = `${prefId}_${printerId}`;
    localStorage.setItem(storageKey, value);
  }
  else{   
    localStorage.setItem(prefId, value)
    }
  }
}