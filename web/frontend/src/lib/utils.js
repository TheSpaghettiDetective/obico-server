export function getNotificationSettingKey(notificationChannel, key) {
  return `${notificationChannel.channelName}_${key}`
}
