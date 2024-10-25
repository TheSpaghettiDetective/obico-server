import { currentThemeValue, defaultTheme, initTheme } from './color-scheme.js'

const theme = {
  value: defaultTheme,
}

let syndicate

// TODO: JusPrin syndicate hack so that we can set branding without add a syndicate to the DB
if (navigator.userAgent.startsWith("JusPrin")) {
  syndicate = { name: 'jusprin' }
} else {
  syndicate = JSON.parse(document.querySelector('#page-context-json').text)['syndicate']
}

// initialize theme for static pages
initTheme(currentThemeValue(theme, syndicate.name), syndicate.name)

// manually control navbar color
let navbar = document.getElementById('dynamic-navbar')
if (navbar) {
  navbar.classList.add('navbar-' + currentThemeValue(theme, syndicate.name).toLowerCase())
}
