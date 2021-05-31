import Vue from 'vue'


// Enum for less errors
export const Themes = {
  Light: 'Light',
  Dark: 'Dark',
  System: 'System',
}


// Default values
export const theme = Vue.observable({
  value: Themes.Dark,
  system: true
})


/**
 * Colors for each theme
 * 
 * Colors usage in CSS:
 * background: rgb(var(--color-bg))
 */
const colors = [
  {name: 'bg', values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#233141'}},
  {name: 'body-bg', values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#2D3E4F'}},
  {name: 'bg-secondary', values: {[Themes.Light]: '#A67DF6', [Themes.Dark]: '#505D6D'}},

  {name: 'footer-bg', values: {[Themes.Light]: '#ACB6C2', [Themes.Dark]: '#000000'}},
  {name: 'footer-text', values: {[Themes.Light]: '#405464', [Themes.Dark]: '#989898'}},

  {name: 'input-bg', values: {[Themes.Light]: '#E9E9E9', [Themes.Dark]: '#FFFFFF'}},
  {name: 'input-text', values: {[Themes.Light]: '#23304B', [Themes.Dark]: '#495057'}},

  {name: 'icon-active', values: {[Themes.Light]: '#A680E5', [Themes.Dark]: '#4B5B69'}},
  {name: 'icon-disabled', values: {[Themes.Light]: '#D3BEF5', [Themes.Dark]: '#A8AEB6'}},

  {name: 'primary', values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#9965f4'}},
  {name: 'gray-200', values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#4E5D6C'}},
  {name: 'gray-200-hover', values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#596a7b'}},

  {name: 'text', values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'text-subdued', values: {[Themes.Light]: '#7E8285', [Themes.Dark]: '#FFFFFF'}},
]

// Converts HEX color to RGB
function HEXtoRGB(color) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color)
  if (!result) { console.log('Wrong HEX value!') }
  return [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
}

// Defines theme by localStorage and/or system settings
export function initTheme() {
  console.log('init theme!')

  let themeValue = localStorage.getItem('colorTheme')
  let themeSystem = themeValue === null || themeValue === Themes.System

  if (themeSystem) {
    if (window.matchMedia('(prefers-color-scheme)').media !== 'not all') {
      themeValue = window.matchMedia('(prefers-color-scheme: light)').matches ? Themes.Light : Themes.Dark
    } else {
      themeValue = Themes.Dark
    }
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