
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
