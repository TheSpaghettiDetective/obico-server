
// Enum with existing color themes for less errors
const Themes = {
  Light: 'Light',
  Dark: 'Dark',
  System: 'System',
}


// Default values
const theme = {
  value: Themes.Dark,
  system: false
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
 * background: rgb(var(--color-background))
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
  {name: 'primary-400',              values: {[Themes.Light]: '#B289F8', [Themes.Dark]: '#9A6AEF'}},
  {name: 'primary',                  values: {[Themes.Light]: '#9965f4', [Themes.Dark]: '#A57BEE'}},
  {name: 'primary-600',              values: {[Themes.Light]: '#874CF0', [Themes.Dark]: '#B18BF3'}},
  {name: 'on-primary',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'secondary',                values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'}},
  {name: 'on-secondary',             values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#28303A'}},

  {name: 'success-400',              values: {[Themes.Light]: '#78D878', [Themes.Dark]: '#4DA04D'}},
  {name: 'success',                  values: {[Themes.Light]: '#6EC66E', [Themes.Dark]: '#5CB85C'}},
  {name: 'on-success',               values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'danger-400',               values: {[Themes.Light]: '#DF706D', [Themes.Dark]: '#D9534F'}},
  {name: 'danger',                   values: {[Themes.Light]: '#D9534F', [Themes.Dark]: '#DF706D'}},
  {name: 'on-danger',                values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'}},

  {name: 'warning-400',              values: {[Themes.Light]: '#FFC677', [Themes.Dark]: '#BF883B'}},
  {name: 'warning',                  values: {[Themes.Light]: '#f0ad4e', [Themes.Dark]: '#C7944B'}},
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

  {name: 'input-background',         values: {[Themes.Light]: '#EEF1F3', [Themes.Dark]: '#37475A'}},

  {name: 'table-accent-1',           values: {[Themes.Light]: '#E3E3E3', [Themes.Dark]: '#27323F'}},
  {name: 'table-accent-2',           values: {[Themes.Light]: '#EDEDED', [Themes.Dark]: '#1B242E'}},

  // Icon colors
  {name: 'icon-tunneling-1',         values: {[Themes.Light]: '#4e5d6c', [Themes.Dark]: '#EAEAEA'}},
  {name: 'icon-tunneling-2',         values: {[Themes.Light]: '#1d2935', [Themes.Dark]: '#CDCDCD'}},
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
function initTheme() {
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

  urls.forEach(function(url) {
    document.documentElement.style.setProperty(`--url-${url.name}`, url.values[themeValue])
  })

  theme.value = themeValue
  theme.system = themeSystem
}

// Selects theme
function selectTheme(newTheme) {
  localStorage.setItem('colorTheme', newTheme)
  initTheme()
}


// initialize theme for static pages
initTheme()

// manually control navbar elements
let navbar = document.getElementById('dynaic-navbar')
let logo = document.getElementById('dynamic-logo')

if (navbar) {
  navbar.classList.add('navbar-' + theme.value.toLowerCase())
}

if (logo) {
  logo.src = '/static/img/navbar-brand/navbar-brand_'+ theme.value.toLowerCase() +'.png'
}