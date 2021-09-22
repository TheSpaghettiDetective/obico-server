/* eslint no-multi-spaces: 0 */

import Vue from 'vue'
import { isLocalStorageSupported } from '@common/utils'


// Enum with existing color themes for less errors
export const Themes = {
  Light: 'Light',
  Dark: 'Dark',
  System: 'System',
}


/**
 * Colors for each theme
 *
 * NOTICE #1:
 * Add colors in full HEX format like "#ffffff". Shortcuts like "#fff" will cause errors.
 *
 * NOTICE #2:
 * If you add new color here, don't forget to add it's default value to main.scss file:
 * 1. Add color into this list
 * 2. Open page in browser
 * 3. Copy calculated css-variable from DevTools (will look like "--color-bg: 35 49 65;")
 * 4. Paste it in main.scss file inside :root styles
 *
 * Colors usage in CSS:
 * background: rgb(var(--color-...))
 *
 * Why translate HEX to RGB?
 * It's a trick to be able to add transparency to any color without creating new variable. For
 * example, primary color "#9965f4" will be trasformed to "153 101 244" (RGB numbers). Since rgb()
 * func allows us to add transparency with "/" after numbers, we can write semi-trasparent primary
 * color as "rgb(153 101 244 / .5)" or using variable "rgb(var(--color-primary) / .5)". If you'll
 * find more elegant way to implement it or you won't need transparency change, feel free to get rid
 * of HEXtoRGB() function and use colors directly.
 *
 * HINT: install 'Color Highlight' VSCode extension to see actual colors here
 */
const colors = [
  {name: 'primary-variant',          values: {[Themes.Light]: '#B289F8', [Themes.Dark]: '#9A6AEF'}},
  {name: 'primary',                  values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#A57BEE'}},
  {name: 'on-primary',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'secondary',                values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'on-secondary',             values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#28303A'}},

  {name: 'success',                  values: {[Themes.Light]: '#5cb85c', [Themes.Dark]: '#5cb85c'}},
  {name: 'success-variant',          values: {[Themes.Light]: '#4CAE4C', [Themes.Dark]: '#4CAE4C'}},
  {name: 'on-success',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'danger',                   values: {[Themes.Light]: '#d9534f', [Themes.Dark]: '#d9534f'}},
  {name: 'danger-variant',           values: {[Themes.Light]: '#C2413D', [Themes.Dark]: '#C2413D'}},
  {name: 'on-danger',                values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'warning',                  values: {[Themes.Light]: '#f0ad4e', [Themes.Dark]: '#f0ad4e'}},
  {name: 'warning-variant',          values: {[Themes.Light]: '#DB9A3F', [Themes.Dark]: '#DB9A3F'}},
  {name: 'on-warning',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},
  {name: 'on-warning-2',             values: {[Themes.Light]: '#000000', [Themes.Dark]: '#000000'}},

  {name: 'background',               values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#233141'}},
  {name: 'surface-primary',          values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#485B71'}},
  {name: 'surface-secondary',        values: {[Themes.Light]: '#f5f5f5', [Themes.Dark]: '#2D3E4F'}},
  {name: 'overlay',                  values: {[Themes.Light]: '#f5f5f5', [Themes.Dark]: '#000000'}},
  {name: 'hover',                    values: {[Themes.Light]: '#666666', [Themes.Dark]: '#ffffff'}},

  {name: 'divider',                  values: {[Themes.Light]: '#ABB6C2', [Themes.Dark]: '#6A7B8A'}},

  {name: 'text-primary',             values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'text-secondary',           values: {[Themes.Light]: '#8A94A2', [Themes.Dark]: '#AAACB0'}},
  {name: 'text-help',                values: {[Themes.Light]: '#4c9be8', [Themes.Dark]: '#4c9be8'}},


  {name: 'input-background',         values: {[Themes.Light]: '#E2E8ED', [Themes.Dark]: '#42566B'}},

  {name: 'table-accent-1',           values: {[Themes.Light]: '#E3E3E3', [Themes.Dark]: '#27323F'}},
  {name: 'table-accent-2',           values: {[Themes.Light]: '#EDEDED', [Themes.Dark]: '#1B242E'}},

  // Icon colors
  {name: 'icon-tunneling-1',         values: {[Themes.Light]: '#4e5d6c', [Themes.Dark]: '#EAEAEA'}},
  {name: 'icon-tunneling-2',         values: {[Themes.Light]: '#1d2935', [Themes.Dark]: '#CDCDCD'}},
  {name: 'icon-navbar-brand',        values: {[Themes.Light]: '#7B8993', [Themes.Dark]: '#ffffff'}},
]

const urls = [
  {
    name: 'logo-bg',
    values: {
      [Themes.Light]: 'url("/static/img/logo-bg/logo-bg_light.svg")',
      [Themes.Dark]: 'url("/static/img/logo-bg/logo-bg_dark.svg")'
    }
  },
  {
    name: 'tail-spin',
    values: {
      [Themes.Light]: 'url("/static/img/tail-spin/tail-spin_light.svg")',
      [Themes.Dark]: 'url("/static/img/tail-spin/tail-spin_dark.svg")'
    }
  },
]

const shadows = [
  {
    name: 'widget',
    values: {
      [Themes.Light]: '0px 3px 30px rgba(0, 0, 0, 0.5)',
      [Themes.Dark]: '0px 3px 30px rgba(0, 0, 0, 0.5)'
    }
  },
  {
    name: 'top-nav',
    values: {
      [Themes.Light]: '0px 2px 10px rgba(0,0,0,0.1)',
      [Themes.Dark]: '0px 2px 10px rgba(0,0,0,.3)'
    }
  },
]


// Converts HEX color to RGB
function HEXtoRGB(color) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color)
  if (!result) { console.log('Wrong HEX value!') }
  return [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
}

// Default value
export const theme = Vue.observable({
  value: (isLocalStorageSupported() ? localStorage.getItem('colorTheme') : Themes.Dark) || Themes.Dark,
})

// Get theme value (exclude "System")
export function getTheme() {
  // Get system settings
  if (theme.value === Themes.System) {
    if (window.matchMedia('(prefers-color-scheme)').media !== 'not all' && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return Themes.Light
    } else {
      return Themes.Dark
    }
  }
  // Return saved value since it's not "System"
  return theme.value
}

// Defines theme by value saved in LocalStorage or system settings
export function initTheme() {
  const themeValue = getTheme()

  colors.forEach(function(color) {
    const RGB = HEXtoRGB(color.values[themeValue])
    document.documentElement.style.setProperty(`--color-${color.name}`, `${RGB[0]} ${RGB[1]} ${RGB[2]}`)
  })

  urls.forEach(function(url) {
    document.documentElement.style.setProperty(`--url-${url.name}`, url.values[themeValue])
  })

  shadows.forEach(function(shadow) {
    document.documentElement.style.setProperty(`--shadow-${shadow.name}`, shadow.values[themeValue])
  })
}

// Selects theme
export function selectTheme(newTheme) {
  theme.value = newTheme

  if (isLocalStorageSupported()) {
    localStorage.setItem('colorTheme', theme.value)
  }

  initTheme()
}
