import moment from 'moment'

// Possible result variants: 56s | 3m | 1h 56m | 2d 1h 56m
export const humanizedDuration = (durationInSeconds) => {
  const seconds = Math.round(durationInSeconds || 0)
  const components = getDurationComponents(seconds)

  if (components.days !== 0) {
    return `${components.days}d ${components.hours + Math.round(components.minutes / 60)}h`
  } else if (components.hours !== 0) {
    return `${components.hours}h ${components.minutes + Math.round(components.seconds / 60)}m`
  } else if (components.minutes !== 0) {
    return `${components.minutes}m ${components.seconds}s`
  } else {
    return `${components.seconds}s`
  }
}

export const getDurationComponents = (durationInSeconds) => {
  const duration = moment.duration(durationInSeconds || 0, 'seconds')
  const days = Math.floor(duration.asDays())
  const hours = duration.hours()
  const minutes = duration.minutes()
  const seconds = duration.seconds()
  return {
    days,
    hours,
    minutes,
    seconds,
  }
}

// Example values: 0m | 1.2m | 1.23m
export const humanizedFilamentUsage = (millimeters) => {
  const meters = (millimeters || 0) / 1000
  const twoDecimal = Math.round(meters * 100) / 100
  return `${twoDecimal}m`
}
