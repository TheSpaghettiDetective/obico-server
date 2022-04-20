// Check if localStorage available
export function isLocalStorageSupported() {
  try {
    const key = '__random_key_we_are_not_going_to_use__'
    localStorage.setItem(key, key)
    localStorage.removeItem(key)
    return true
  } catch (e) {
    return false
  }
}
