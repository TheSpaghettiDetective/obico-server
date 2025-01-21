import Vue from 'vue'
import { isLocalStorageSupported } from '@static/js/utils'
import {
  currentThemeValue as themeValue,
  defaultTheme,
  initTheme as init,
} from '@static/js/color-scheme'

export const theme = Vue.observable({
  value: defaultTheme,
})

export function currentThemeValue(syndicate) {
  return themeValue(theme, syndicate)
}

export function initTheme() {
  return init(currentThemeValue(Vue.prototype.$syndicate), Vue.prototype.$syndicate)
}

export function setTheme(newTheme) {
  theme.value = newTheme
  if (isLocalStorageSupported()) {
    localStorage.setItem('colorTheme', theme.value)
  }
  initTheme(Vue.prototype.$syndicate)
}
