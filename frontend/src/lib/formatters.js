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
    const minutesRounded = components.minutes + Math.round(components.seconds / 60)
    if (minutesRounded === 60) {
      const hoursRounded = components.hours + 1
      if (hoursRounded === 24) {
        return `${1}d ${0}h`
      } else {
        return `${components.hours + 1}h ${0}m`
      }
    } else {
      return `${components.hours}h ${minutesRounded}m`
    }
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

export const humanizedFilamentUsage = (millimeters) => {
  const meters = (millimeters || 0) / 1000
  const twoDecimal = Math.round(meters * 100) / 100
  return `${twoDecimal}m`
}

export const timeFromNow = (duration) => {
  if (!duration) {
    return '-'
  }
  const timeFormat = 'h:mm a (MMM D, YYYY)'
  let date = new Date()
  let newDate = new Date(date.setSeconds(date.getSeconds() + duration))
  return moment(newDate).format(timeFormat)
}
