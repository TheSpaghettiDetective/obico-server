/* eslint no-multi-spaces: 0 */

import Vue from 'vue'


// Enum with existing color themes for less errors
export const Themes = {
  Light: 'Light',
  Dark: 'Dark',
  System: 'System',
}


// Default values
export const theme = Vue.observable({
  value: Themes.Dark,
  system: false
})


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
 * background: rgb(var(--color-body-bg-d-10))
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
  {name: 'primary-400',              values: {[Themes.Light]: '#B289F8', [Themes.Dark]: '#9A6AEF'}}, // MEMO: in case of change check slider at printer's settings
  {name: 'primary',                  values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#A57BEE'}}, // assuming as "primary-500"
  {name: 'primary-600',              values: {[Themes.Light]: '#874CF0', [Themes.Dark]: '#B18BF3'}},

  {name: 'success',                  values: {[Themes.Light]: '#5cb85c', [Themes.Dark]: '#5cb85c'}},
  {name: 'danger',                   values: {[Themes.Light]: '#df706d', [Themes.Dark]: '#d9534f'}},

  {name: 'warning',                  values: {[Themes.Light]: '#f0ad4e', [Themes.Dark]: '#f0ad4e'}},
  {name: 'on-warning',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},
  {name: 'on-warning-2',             values: {[Themes.Light]: '#000000', [Themes.Dark]: '#000000'}},

  {name: 'background',               values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#233141'}},
  {name: 'surface-primary',          values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#485B71'}},
  {name: 'surface-secondary',        values: {[Themes.Light]: '#f5f5f5', [Themes.Dark]: '#2D3E4F'}},
  {name: 'overlay',                  values: {[Themes.Light]: '#f5f5f5', [Themes.Dark]: '#000000'}},
  {name: 'hover',                    values: {[Themes.Light]: '#666666', [Themes.Dark]: '#ffffff'}},

  {name: 'divider',                  values: {[Themes.Light]: '#abb6c2', [Themes.Dark]: '#334A62'}},

  {name: 'text-primary',             values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'text-secondary',           values: {[Themes.Light]: '#8A94A2', [Themes.Dark]: '#AAACB0'}},

  // Toggle
  {name: 'toggle-background',        values: {[Themes.Light]: '#A67DF6', [Themes.Dark]: '#37475A'}},
  {name: 'toggle-icon-active',       values: {[Themes.Light]: '#A680E5', [Themes.Dark]: '#4B5B69'}},
  {name: 'toggle-icon-disabled',     values: {[Themes.Light]: '#D3BEF5', [Themes.Dark]: '#A8AEB6'}},




  {name: 'primary-light',            values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#EBEBEB'}},
  {name: 'gray-200-hover',           values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#596a7b'}},
  {name: 'white-d-60',               values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#666666'}},
  {name: 'bg-dark-d-10',             values: {[Themes.Light]: '#9A65F4', [Themes.Dark]: '#17222c'}},




  {name: 'input-bg',                 values: {[Themes.Light]: '#E9E9E9', [Themes.Dark]: '#FFFFFF'}},
  {name: 'input-text',               values: {[Themes.Light]: '#23304B', [Themes.Dark]: '#495057'}},
  {name: 'input-dark-bg',            values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#4E5D6C'}},


  {name: 'text',                     values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'text-subdued',             values: {[Themes.Light]: '#7E8285', [Themes.Dark]: '#FFFFFF'}},
  {name: 'text-inverted',            values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#28303A'}},

  {name: 'color',                    values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#FFFFFF'}},
  {name: 'color-2',                  values: {[Themes.Light]: '#CCCCCC', [Themes.Dark]: '#CCCCCC'}},


  // From SASS variables

  {name: 'gray-100',                 values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'gray-200',                 values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#4E5D6C'}},
  {name: 'gray-200-2',               values: {[Themes.Light]: '#cccccc', [Themes.Dark]: '#4E5D6C'}},
  {name: 'gray-600',                 values: {[Themes.Light]: '#868e96', [Themes.Dark]: '#868e96'}},

  {name: 'form-bg',                  values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#2b3e50'}},
  {name: 'body-bg',                  values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#2B3E50'}},
  {name: 'body-bg-darker',           values: {[Themes.Light]: '#f6f9fc', [Themes.Dark]: '#2B3E50'}},
  {name: 'bg-dark',                  values: {[Themes.Light]: '#f5f5f5', [Themes.Dark]: '#293b4d'}},
  {name: 'white',                    values: {[Themes.Light]: '#000000', [Themes.Dark]: '#FFFFFF'}},
  {name: 'dark-white',               values: {[Themes.Light]: '#2B3E50', [Themes.Dark]: '#FFFFFF'}},
  {name: 'black',                    values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#000000'}},
  
  {name: 'border',                  values: {[Themes.Light]: '#abb6c2', [Themes.Dark]: '#666666'}},


  // Derivatives from SASS functions (lighted, darken, etc.)

  {name: 'body-bg-l-10',             values: {[Themes.Light]: '#e6e6e6', [Themes.Dark]: '#3d5871'}},
  {name: 'body-bg-l-5p',             values: {[Themes.Light]: '#F1F1F1', [Themes.Dark]: '#344b61'}},
  {name: 'body-bg-l-3',              values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#30465a'}},
  {name: 'body-bg-d-5',              values: {[Themes.Light]: '#f2f2f2', [Themes.Dark]: '#22313f'}},
  {name: 'body-bg-d-10',             values: {[Themes.Light]: '#e6e6e6', [Themes.Dark]: '#19242f'}},
  {name: 'body-bg-d-10-darker',      values: {[Themes.Light]: '#b8b8b8', [Themes.Dark]: '#19242f'}},
  {name: 'body-bg-d-10-lighter',     values: {[Themes.Light]: '#E7E7E7', [Themes.Dark]: '#252F3A'}},

  {name: 'gray-100-d-20',            values: {[Themes.Light]: '#9f9f9f', [Themes.Dark]: '#b8b8b8'}},
  {name: 'gray-100-d-30',            values: {[Themes.Light]: '#b8b8b8', [Themes.Dark]: '#9f9f9f'}},

  // Icon colors
  {name: 'icon-tunneling-tone-1',    values: {[Themes.Light]: '#4e5d6c', [Themes.Dark]: '#EAEAEA'}},
  {name: 'icon-tunneling-tone-2',    values: {[Themes.Light]: '#1d2935', [Themes.Dark]: '#CDCDCD'}},
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

// Converts HEX color to RGB
function HEXtoRGB(color) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color)
  if (!result) { console.log('Wrong HEX value!') }
  return [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
}

// Defines theme by value saved in LocalStorage or system settings
export function initTheme() {
  console.log('Init theme')

  let themeValue = localStorage.getItem('colorTheme')
  let themeSystem = themeValue === Themes.System
  // let themeSystem = themeValue === null || themeValue === Themes.System

  if (themeSystem) {
    if (window.matchMedia('(prefers-color-scheme)').media !== 'not all') {
      themeValue = window.matchMedia('(prefers-color-scheme: light)').matches ? Themes.Light : Themes.Dark
    } else {
      themeValue = Themes.Dark
    }
  }

  if (themeValue === null) {
    themeValue = theme.value // Set default value
  }

  colors.forEach(function(color) {
    const RGB = HEXtoRGB(color.values[themeValue])
    console.log(color.name, color.values[themeValue], RGB)
    document.documentElement.style.setProperty(`--color-${color.name}`, `${RGB[0]} ${RGB[1]} ${RGB[2]}`)
  })

  urls.forEach(function(url) {
    document.documentElement.style.setProperty(`--url-${url.name}`, url.values[themeValue])
  })

  theme.value = themeValue
  theme.system = themeSystem
}

// Selects theme
export function selectTheme(newTheme) {
  localStorage.setItem('colorTheme', newTheme)
  initTheme()
}
