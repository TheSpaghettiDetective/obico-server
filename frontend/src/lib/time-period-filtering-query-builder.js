import moment from 'moment'

const DateParamFormat = 'YYYY-MM-DD'
export default (val, dateFrom, dateTo, user) => {
  let params = {}
  const today = new Date()
  const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()))
  const lastDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay() + 6))

  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  const firstDayOfYear = new Date(today.getFullYear(), 0, 1)
  const lastDayOfYear = new Date(today.getFullYear(), 11, 31)

  switch (val) {
    case 'this_week':
      params = {
        from_date: moment(firstDayOfWeek).format(DateParamFormat),
        to_date: moment(lastDayOfWeek).format(DateParamFormat),
      }
      break
    case 'this_month':
      params = {
        from_date: moment(firstDayOfMonth).format(DateParamFormat),
        to_date: moment(lastDayOfMonth).format(DateParamFormat),
      }
      break
    case 'this_year':
      params = {
        from_date: moment(firstDayOfYear).format(DateParamFormat),
        to_date: moment(lastDayOfYear).format(DateParamFormat),
      }
      break
    case 'custom':
      if (dateFrom) {
        params['from_date'] = moment(dateFrom).format(DateParamFormat)
      }
      if (dateTo) {
        params['to_date'] = moment(dateTo).format(DateParamFormat)
      }
      break
    default:
      return {}
  }
  params['from_date'] = params['from_date'] || moment(user.date_joined).format(DateParamFormat)
  params['to_date'] = params['to_date'] || moment(new Date()).format(DateParamFormat)
  params['timezone'] = Intl.DateTimeFormat().resolvedOptions().timeZone
  return params
}
