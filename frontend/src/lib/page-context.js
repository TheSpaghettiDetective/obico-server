export const pageContext = () => {
  const context = JSON.parse(document.querySelector('#page-context-json').text)
  console.log('DEBUG: Full page context:', context)
  return context
}

export const mobilePlatform = () => {
  return pageContext()['app_platform']
}

export const inMobileWebView = () => {
  return mobilePlatform() !== ''
}

export const user = () => {
  return JSON.parse(document.querySelector('#user-json').text)
}

export const settings = () => {
  return JSON.parse(document.querySelector('#settings-json').text)
}

export const syndicate = () => {
  return pageContext()['syndicate']
}

export const language = () => {
  const lang = pageContext()['language']
  console.log('DEBUG: Language from page context:', lang)
  return lang
}