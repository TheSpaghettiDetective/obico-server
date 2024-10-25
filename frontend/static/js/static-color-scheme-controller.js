import { currentThemeValue, defaultTheme, initTheme } from './color-scheme.js'

const theme = {
  value: defaultTheme,
}

const syndicate = JSON.parse(document.querySelector('#page-context-json').text)['syndicate']

// initialize theme for static pages
initTheme(currentThemeValue(theme, syndicate.name), syndicate.name)

// manually control navbar color
let navbar = document.getElementById('dynamic-navbar')
if (navbar) {
  navbar.classList.add('navbar-' + currentThemeValue(theme, syndicate.name).toLowerCase())
}
