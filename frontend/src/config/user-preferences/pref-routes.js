import notificationPlugins from '@src/notifications/plugins'

const defaultRoutes = {
  GeneralPreferences: '/user_preferences/general/',
  ThemePreferences: '/user_preferences/personalization/',
  ProfilePreferences: '/user_preferences/profile/',
  AuthorizedApps: '/user_preferences/authorized_apps/',
  GeneralNotifications: '/user_preferences/general_notifications/',
  PushNotifications: '/user_preferences/mobile_push_notifications/',
}

const notificationRoutes = Object.keys(notificationPlugins).reduce((obj, name) => {
  return Object.assign(obj, { [name]: `/user_preferences/notification_${name}/` })
}, {})

export default {
  ...defaultRoutes,
  ...notificationRoutes,
}
