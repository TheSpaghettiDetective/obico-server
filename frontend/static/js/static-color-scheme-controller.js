import { currentThemeValue, defaultTheme, initTheme } from './color-scheme.js'

const theme = {
  value: defaultTheme,
}

const urlParams = new URLSearchParams(window.location.search)
const brand = urlParams.get('theme')

// initialize theme for static pages
initTheme(currentThemeValue(theme), brand)

// manually control navbar color
let navbar = document.getElementById('dynamic-navbar')
if (navbar) {
  navbar.classList.add('navbar-' + currentThemeValue(theme).toLowerCase())
}
