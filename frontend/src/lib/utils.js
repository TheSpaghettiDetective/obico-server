import startCase from 'lodash/startCase'
import toLower from 'lodash/toLower'
import replace from 'lodash/replace'
import get from 'lodash/get'
import moment from 'moment'

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
      onData(e.srcElement.result)
    })
    reader.readAsArrayBuffer(maybeBin)
  } else {
    onData(maybeBin)
  }
}

export const getCsrfFromDocument = () => {
  return document.getElementsByName('csrfmiddlewaretoken')[0]?.value
}

export const downloadFile = (url, filename) => {
  fetch(url)
    .then((res) => res.blob())
    .then((res) => {
      const aElement = document.createElement('a')
      aElement.setAttribute('download', filename)
      const href = URL.createObjectURL(res)
      aElement.href = href
      aElement.setAttribute('target', '_blank')
      aElement.click()
      URL.revokeObjectURL(href)
    })
}

export const getHumanizedDuration = (timeInSeconds) => {
  const components = getDurationComponents(timeInSeconds)

  let result = ''
  if (components.days !== 0) {
    result += `${components.days}d `
  }
  if (components.days !== 0 || components.hours !== 0) {
    result += `${components.hours}h `
  }

  result += `${components.minutes}m`
  return result
}

export const getDurationComponents = (timeInSeconds) => {
  const duration = moment.duration(timeInSeconds, 'seconds')

  const days = Math.floor(duration.asDays())
  const hours = duration.hours()
  const minutes = duration.minutes()

  return {
    days,
    hours,
    minutes,
  }
}
