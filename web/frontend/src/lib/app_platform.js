
export const isMobile = function() {
    return JSON.parse(document.querySelector('#app-platform-json').text)['platform'] !== ''
}

export const isIOS = function() {
    JSON.parse(document.querySelector('#app-platform-json').text)['platform'] === 'ios'
}
