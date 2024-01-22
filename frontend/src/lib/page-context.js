export const mobilePlatform = () => {
  return JSON.parse(document.querySelector('#app-platform-json').text)['platform']
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
  return JSON.parse(document.querySelector('#syndicate-json').text)
}

export const onlyNotifications = () => {
  return new URLSearchParams(window.location.search).get('onlyNotifications') === 'true'
}

export const onlyName = () => {
  return new URLSearchParams(window.location.search).get('onlyName') === 'true'
}
