
export const getLocalPref = (prefId, defaultValue) => {
    var val = localStorage.getItem(prefId) || defaultValue
    // Hack to deal with data type such as boolean and number
    try {
      return JSON.parse(val)
    } catch (e) {
      return val
    }
  }

export const setLocalPref = (prefId, value) => {
    return localStorage.setItem(prefId, value)
}
