
export const isMobile = () => {
    return JSON.parse(document.querySelector('#app-platform-json').text)['platform'] !== ''
}

export const isIOS = () => {
    return JSON.parse(document.querySelector('#app-platform-json').text)['platform'] === 'ios'
}
