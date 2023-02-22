import moment from 'moment'

const DateParamFormat = 'YYYY-MM-DD'

export const queryBuilder = (filterValue, customDateFrom, customDateTo, user) => {
  return {
    from_date: getDateFrom(filterValue, customDateFrom, user).format(DateParamFormat),
    to_date: getDateTo(filterValue, customDateTo).format(DateParamFormat),
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  }
}

export const getDateFrom = (filterValue, customDateFrom, user) => {
  const today = new Date()
  const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()))
  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1)

  switch (filterValue) {
    case 'this_week':
      return moment(firstDayOfWeek)
    case 'this_month':
      return moment(firstDayOfMonth)
    case 'this_year':
      return moment(firstDayOfYear)
    case 'custom':
      if (customDateFrom) {
        return moment(customDateFrom)
      }
  }
  return moment(user.date_joined)
}

export const getDateTo = (filterValue, customDateTo) => {
  const today = new Date()
  const lastDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay() + 6))
  const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  const lastDayOfYear = new Date(today.getFullYear(), 11, 31)

  switch (filterValue) {
    case 'this_week':
      return moment(lastDayOfWeek)
    case 'this_month':
      return moment(lastDayOfMonth)
    case 'this_year':
      return moment(lastDayOfYear)
    case 'custom':
      if (customDateTo) {
        return moment(customDateTo)
      }
  }
  return moment()
}

export const getRecommendedGrouping = (filterValue, customDateFrom, customDateTo, user) => {
  const fromDate = getDateFrom(filterValue, customDateFrom, user)
  const toDate = getDateTo(filterValue, customDateTo)
  const diff = toDate.diff(fromDate, 'days')
  if (diff <= 31) {
    return 'day'
  } else if (diff <= 95) {
    return 'week'
  } else if (diff <= 366) {
    return 'month'
  } else {
    return 'year'
  }
}
