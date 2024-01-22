import { currentThemeValue, defaultTheme, initTheme } from './color-scheme.js'

const theme = {
  value: defaultTheme,
}

const syndicate = JSON.parse(document.querySelector('#syndicate-json').text)

// initialize theme for static pages
initTheme(currentThemeValue(theme), syndicate.provider)

// manually control navbar color
let navbar = document.getElementById('dynamic-navbar')
if (navbar) {
  navbar.classList.add('navbar-' + currentThemeValue(theme).toLowerCase())
}
