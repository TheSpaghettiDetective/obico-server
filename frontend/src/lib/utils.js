import startCase from 'lodash/startCase'
import toLower from 'lodash/toLower'
import replace from 'lodash/replace'


export function getNotificationSettingKey(notificationChannel, key) {
  return `${notificationChannel.channelName}_${key}`
}

export function temperatureDisplayName(name) {
  return startCase(toLower(replace(name, /_/g, ' ')))
}
