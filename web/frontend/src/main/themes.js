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
 * color as "rgb(153 101 244 / .5)" or using variable "rgb(var(--color-tsd-purple) / .5)". If you'll
 * find more elegant way to implement it or you won't need transparency change, feel free to get rid
 * of HEXtoRGB() function and use colors directly.
 *
 * HINT: install 'Color Highlight' VSCode extension to see actual colors here
 */
const colors = [
  // Synced with style guide

  {name: 'page-background',          values: {[Themes.Light]: '#ebebeb', [Themes.Dark]: '#23313f'}},
  {name: 'medium-background',        values: {[Themes.Light]: '#f6f9fc', [Themes.Dark]: '#2d3e4f'}},
  {name: 'light-background',         values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#4e5d6c'}},

  {name: 'dividers',                 values: {[Themes.Light]: '#abb6c2', [Themes.Dark]: '#4e5d6c'}},

  {name: 'main-text',                values: {[Themes.Light]: '#1d2935', [Themes.Dark]: '#ffffff'}},
  {name: 'less-emphasis-body-text',  values: {[Themes.Light]: '#425466', [Themes.Dark]: '#4e5d6c'}},

  {name: 'tsd-purple',               values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#9965f4'}},
  {name: 'warning-yellow',           values: {[Themes.Light]: '#f0ad4e', [Themes.Dark]: '#f0ad4e'}},
  {name: 'positive-green',           values: {[Themes.Light]: '#5cb85c', [Themes.Dark]: '#5cb85c'}},
  {name: 'negative-red',             values: {[Themes.Light]: '#d9534f', [Themes.Dark]: '#d9534f'}},
  {name: 'neutral-grey',             values: {[Themes.Light]: '#abb6c2', [Themes.Dark]: '#abb6c2'}},

  {name: 'overlay',                  values: {[Themes.Light]: '#fafafa', [Themes.Dark]: '#000000'}},
  {name: 'overlay-2',                values: {[Themes.Light]: '#000000', [Themes.Dark]: '#000000'}},


  // To get rid of...

  {name: 'bg-video',                 values: {[Themes.Light]: '#ADB7C3', [Themes.Dark]: '#000000'}},
  {name: 'bg-body',                  values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#2D3E4F'}},

  {name: 'bg-secondary',             values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#505D6D'}},
  {name: 'icon-active',              values: {[Themes.Light]: '#A680E5', [Themes.Dark]: '#4B5B69'}},
  {name: 'icon-disabled',            values: {[Themes.Light]: '#D3BEF5', [Themes.Dark]: '#A8AEB6'}},

  {name: 'footer-bg',                values: {[Themes.Light]: '#ACB6C2', [Themes.Dark]: '#000000'}},
  {name: 'footer-text',              values: {[Themes.Light]: '#405464', [Themes.Dark]: '#989898'}},

  {name: 'input-bg',                 values: {[Themes.Light]: '#E9E9E9', [Themes.Dark]: '#FFFFFF'}},
  {name: 'input-text',               values: {[Themes.Light]: '#23304B', [Themes.Dark]: '#495057'}},
  {name: 'input-dark-bg',            values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#4E5D6C'}},

  {name: 'white-primary',            values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#9965f4'}},
  {name: 'primary-white',            values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#FFFFFF'}},
  {name: 'primary-light',            values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#EBEBEB'}},

  {name: 'text-subdued',             values: {[Themes.Light]: '#7E8285', [Themes.Dark]: '#FFFFFF'}},
  
  {name: 'text-inverted',            values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#28303A'}},

  {name: 'gray-200-hover',           values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#596a7b'}},

  {name: 'body-bg-darker',           values: {[Themes.Light]: '#f6f9fc', [Themes.Dark]: '#2B3E50'}},

  {name: 'white',                    values: {[Themes.Light]: '#000000', [Themes.Dark]: '#FFFFFF'}},

  {name: 'primary-l-10',             values: {[Themes.Light]: '#b995f7', [Themes.Dark]: '#b995f7'}},
  {name: 'primary-l-7',              values: {[Themes.Light]: '#af86f6', [Themes.Dark]: '#af86f6'}},
  {name: 'primary-d-10',             values: {[Themes.Light]: '#7935f1', [Themes.Dark]: '#7935f1'}},
  {name: 'primary-d-20',             values: {[Themes.Light]: '#5d10e3', [Themes.Dark]: '#5d10e3'}},
  {name: 'primary-d-35',             values: {[Themes.Light]: '#400b9b', [Themes.Dark]: '#400b9b'}},

  {name: 'body-bg-l-5p',             values: {[Themes.Light]: '#F1F1F1', [Themes.Dark]: '#344b61'}},
  {name: 'body-bg-l-3',              values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#30465a'}},
  {name: 'body-bg-d-5',              values: {[Themes.Light]: '#f2f2f2', [Themes.Dark]: '#22313f'}},
  {name: 'body-bg-d-10',             values: {[Themes.Light]: '#e6e6e6', [Themes.Dark]: '#19242f'}},
  {name: 'body-bg-d-10-darker',      values: {[Themes.Light]: '#b8b8b8', [Themes.Dark]: '#19242f'}},
  {name: 'body-bg-d-10-lighter',     values: {[Themes.Light]: '#E7E7E7', [Themes.Dark]: '#252F3A'}},

  {name: 'white-d-60',               values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#666666'}},

  {name: 'bg-dark-d-10',             values: {[Themes.Light]: '#9A65F4', [Themes.Dark]: '#17222c'}},

  // print shot feedback - unvisited page
  {name: 'gray-100-d-20',            values: {[Themes.Light]: '#9f9f9f', [Themes.Dark]: '#b8b8b8'}},
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
    document.documentElement.style.setProperty(`--color-${color.name}`, `${RGB[0]} ${RGB[1]} ${RGB[2]}`)
  })

  theme.value = themeValue
  theme.system = themeSystem
}

// Selects theme
export function selectTheme(newTheme) {
  localStorage.setItem('colorTheme', newTheme)
  initTheme()
}
