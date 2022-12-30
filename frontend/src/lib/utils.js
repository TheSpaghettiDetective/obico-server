import startCase from 'lodash/startCase'
import toLower from 'lodash/toLower'
import replace from 'lodash/replace'
import get from 'lodash/get'

export function getNotificationSettingKey(notificationChannel, key) {
  return `${notificationChannel.channelName}_${key}`
}

export function temperatureDisplayName(name) {
  return startCase(toLower(replace(name, /_/g, ' ')))
}

export const getNormalizedP = (predictions, currentPosition, isPublic) => {
  const num = Math.round(predictions.length * currentPosition)
  const propName = isPublic ? 'p' : 'fields.normalized_p'
  return get(predictions[num], `${propName}`, 0)
}

export const toArrayBuffer = (maybeBin, onData) => {
  if (!maybeBin) {
    return
  }

  if (maybeBin instanceof Blob) {
    const reader = new FileReader()
    reader.addEventListener('loadend', (e) => {
      if (!e.srcElement) {
        return
      }
      onData(e.srcElement.result);
    })
    reader.readAsArrayBuffer(maybeBin)
  } else {
    onData(maybeBin)
  }
}

export const getCsrfFromDocument = () => {
  return document.getElementsByName('csrfmiddlewaretoken')[0]?.value
}

export const wasElementClicked = (event, className) => {
  let clicked = false
  const path = event.path || (event.composedPath && event.composedPath())
  
  for (const node of path) {
    if (node.className && node.className.includes(className)) {
      clicked = true
      break
    }
  }

  return clicked
}
