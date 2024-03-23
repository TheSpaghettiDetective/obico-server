import routes from '@config/user-preferences/routes'
import notificationPlugins from '@src/notifications/plugins'
import { inMobileWebView } from '@src/lib/page-context'


const onlyNotifications =
  new URLSearchParams(window.location.search).get('onlyNotifications') === 'true'

const defaultSections = {
  GeneralPreferences: {
    title: 'General',
    faIcon: 'fas fa-cog',
    importComponent: () => import('@src/components/user-preferences/GeneralPreferences'),
    route: routes.GeneralPreferences,
    isHidden: inMobileWebView() || onlyNotifications,
  },
  ThemePreferences: {
    title: 'Appearance',
    faIcon: 'fas fa-magic',
    importComponent: () => import('@src/components/user-preferences/ThemePreferences'),
    route: routes.ThemePreferences,
    isHidden:
      (inMobileWebView() &&
        !(new URLSearchParams(window.location.search).get('themeable') === 'true')) ||
      onlyNotifications,
  },
  ProfilePreferences: {
    title: 'Profile',
    faIcon: 'fas fa-user-edit',
    importComponent: () => import('@src/components/user-preferences/ProfilePreferences'),
    route: routes.ProfilePreferences,
    isHidden: onlyNotifications,
  },
  AuthorizedApps: {
    title: 'Authorized Apps',
    faIcon: 'fas fa-check-circle',
    importComponent: () => import('@src/components/user-preferences/AuthorizedApps'),
    route: routes.AuthorizedApps,
    isHidden: onlyNotifications,
  },

  // Notifications
  GeneralNotifications: {
    title: 'Notifications',
    faIcon: 'fas fa-bell',
    importComponent: () =>
      import('@src/components/user-preferences/notifications/GeneralNotifications'),
    route: routes.GeneralNotifications,
  },
  PushNotifications: {
    title: 'Push Notification',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => ({}),
    route: routes.PushNotifications,
    isHidden: !inMobileWebView(),
  },
}

const notificationSections = Object.keys(notificationPlugins).reduce((obj, name) => {
  return Object.assign(obj, {
    [name]: {
      title: notificationPlugins[name].displayName,
      channelName: name,
      isSubcategory: true,
      isNotificationChannel: true,
      route: routes[name],
      importComponent: () =>
        import('@src/notifications/plugins/' + notificationPlugins[name].componentName),
    },
  })
}, {})

export default {
  ...defaultSections,
  ...notificationSections,
}
