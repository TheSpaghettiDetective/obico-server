export const pageContext = () => {
  return JSON.parse(document.querySelector('#page-context-json').text)
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
  return pageContext()['language']
}