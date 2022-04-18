import { currentThemeValue, defaultTheme, initTheme } from './color-scheme.js'

const theme = {
  value: defaultTheme,
}

// initialize theme for static pages
initTheme(theme.value)

// manually control navbar color
let navbar = document.getElementById('dynamic-navbar')
if (navbar) {
  navbar.classList.add('navbar-' + currentThemeValue(theme).toLowerCase())
}
