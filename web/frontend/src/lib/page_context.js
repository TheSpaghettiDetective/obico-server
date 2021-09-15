
export const isMobile = () => {
    return JSON.parse(document.querySelector('#app-platform-json').text)['platform'] !== ''
}
