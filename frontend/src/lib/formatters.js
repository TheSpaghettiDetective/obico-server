import moment from 'moment'

// Possible result variants: 56s | 3m | 1h 56m | 2d 1h 56m
export const humanizedDuration = (timeInSeconds) => {
  const seconds = Math.round(timeInSeconds || 0)
  if (seconds < 60) {
    return `${seconds}s`
  }

  const components = getDurationComponents(seconds)
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

export const getDurationComponents = (seconds) => {
  const duration = moment.duration(seconds || 0, 'seconds')
  const days = Math.floor(duration.asDays())
  const hours = duration.hours()
  const minutes = duration.minutes()
  return {
    days,
    hours,
    minutes,
  }
}

// Possible result variants: 0m | 1.2m | 1.23m
export const humanizedFilamentUsage = (millimeters) => {
  const meters = (millimeters || 0) / 1000
  const twoDecimal = Math.round(meters * 100) / 100
  return `${twoDecimal}m`
}
