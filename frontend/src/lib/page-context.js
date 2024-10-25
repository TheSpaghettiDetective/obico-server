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
  let syndicate

  // TODO: JusPrin syndicate hack so that we can set branding without add a syndicate to the DB
  if (navigator.userAgent.startsWith("JusPrin")) {
    syndicate = { name: 'jusprin' }
  } else {
    syndicate = pageContext()['syndicate']
  }

  return syndicate
}

export const language = () => {
  return pageContext()['language']
}