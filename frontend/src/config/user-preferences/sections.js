import routes from '@config/user-preferences/routes'
import { inMobileWebView, onlyNotifications } from '@src/lib/page_context'

export default {
  ThemePreferences: {
    title: 'Appearance',
    faIcon: 'fas fa-magic',
    importComponent: () => import('@src/components/user-preferences/ThemePreferences'),
    route: routes.ThemePreferences,
    isHidden: (inMobileWebView() && !(new URLSearchParams(window.location.search).get('themeable') === 'true')) || onlyNotifications(),
  },
  ProfilePreferences: {
    title: 'Profile',
    faIcon: 'fas fa-user-edit',
    importComponent: () => import('@src/components/user-preferences/ProfilePreferences'),
    route: routes.ProfilePreferences,
    isHidden: onlyNotifications(),
  },
  AuthorizedApps: {
    title: 'Authorized Apps',
    faIcon: 'fas fa-check-circle',
    importComponent: () => import('@src/components/user-preferences/AuthorizedApps'),
    route: routes.AuthorizedApps,
    isHidden: onlyNotifications(),
  },

  // Notifications
  GeneralNotifications: {
    title: 'Notifications',
    faIcon: 'fas fa-bell',
    importComponent: () => import('@src/components/user-preferences/notifications/GeneralNotifications'),
    route: routes.GeneralNotifications,
  },
  PushNotifications: {
    title: 'Push Notifications',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => ({}),
    route: routes.PushNotifications,
    isHidden: !inMobileWebView(),
  },
  EmailNotifications: {
    title: 'Email',
    channelName: 'email',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/EmailNotifications'),
    route: routes.EmailNotifications,
  },
  SmsNotifications: {
    title: 'SMS',
    channelName: 'twillio',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/SmsNotifications'),
    route: routes.SmsNotifications,
  },
  PushbulletNotifications: {
    title: 'Pushbullet',
    channelName: 'pushbullet',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/PushbulletNotifications'),
    route: routes.PushbulletNotifications,
  },
  DiscordNotifications: {
    title: 'Discord',
    channelName: 'discord',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/DiscordNotifications'),
    route: routes.DiscordNotifications,
  },
  TelegramNotifications: {
    title: 'Telegram',
    channelName: 'telegram',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/TelegramNotifications'),
    route: routes.TelegramNotifications,
  },
  PushoverNotifications: {
    title: 'Pushover',
    channelName: 'pushover',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/PushoverNotifications'),
    route: routes.PushoverNotifications,
  },
  SlackNotifications: {
    title: 'Slack',
    channelName: 'slack',
    isSubcategory: true,
    isNotificationChannel: true,
    importComponent: () => import('@src/components/user-preferences/notifications/SlackNotifications'),
    route: routes.SlackNotifications,
  },
}
