import moment from 'moment'

export const humanizedDuration = (durationInSeconds) => {
  const seconds = Math.round(durationInSeconds || 0)
  const components = getDurationComponents(seconds)

  if (components.days !== 0) {
    const hoursRounded = components.hours + Math.round(components.minutes / 60)
    if (hoursRounded === 24) {
      return `${components.days + 1}d ${0}h`
    } else {
      return `${components.days}d ${hoursRounded}h`
    }
  } else if (components.hours !== 0) {
    if (components.minutes === 60) {
      const hoursRounded = components.hours + 1
      if (hoursRounded === 24) {
        return `${1}d ${0}h`
      } else {
        return `${components.hours + 1}h ${0}m`
      }
    } else {
      return `${components.hours}h ${components.minutes}m`
    }
  } else {
    return `${components.minutes}m`
  }
}

export const getDurationComponents = (durationInSeconds) => {
  const duration = moment.duration(durationInSeconds || 0, 'seconds')
  const days = Math.floor(duration.asDays())
  const hours = duration.hours()
  const minutes = duration.minutes() + Math.round(duration.seconds() / 60)
  return {
    days,
    hours,
    minutes,
  }
}

export const humanizedFilamentUsage = (millimeters) => {
  const meters = (millimeters || 0) / 1000
  const twoDecimal = Math.round(meters * 100) / 100
  return `${twoDecimal}m`
}

export const timeFromNow = (duration, timeFormat = 'MMM D, h:mm a') => {
  if (!duration) {
    return '-'
  }
  let date = new Date()
  let newDate = new Date(date.setSeconds(date.getSeconds() + duration))
  return moment(newDate).format(timeFormat)
}
