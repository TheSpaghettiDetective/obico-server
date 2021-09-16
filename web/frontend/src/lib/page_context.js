
export const inMobileWebView = () => {
    return JSON.parse(document.querySelector('#app-platform-json').text)['platform'] !== ''
}
