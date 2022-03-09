import routes from '@config/user-preferences/routes'
import { settings } from '@src/lib/page_context'
import { inMobileWebView, onlyNotifications } from '@src/lib/page_context'

const { SLACK_CLIENT_ID, PUSHOVER_APP_TOKEN } = settings()

export default {
  ThemePreferences: {
    title: 'Color Scheme',
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

  // Notificatons
  GeneralNotifications: {
    title: 'Notifications',
    faIcon: 'fas fa-bell',
    importComponent: () => import('@src/components/user-preferences/GeneralNotifications'),
    route: routes.GeneralNotifications,
  },
  PushNotifications: {
    title: 'Push Notifications',
    isSubcategory: true,
    importComponent: () => ({}),
    route: routes.PushNotifications,
    isHidden: !inMobileWebView(),
  },
  EmailNotifications: {
    title: 'Email',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/EmailNotifications'),
    route: routes.EmailNotifications,
  },
  SmsNotifications: {
    title: 'SMS',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/SmsNotifications'),
    route: routes.SmsNotifications,
  },
  PushbulletNotifications: {
    title: 'Pushbullet',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/PushbulletNotifications'),
    route: routes.PushbulletNotifications,
  },
  DiscordNotifications: {
    title: 'Discord',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/DiscordNotifications'),
    route: routes.DiscordNotifications,
  },
  TelegramNotifications: {
    title: 'Telegram',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/TelegramNotifications'),
    route: routes.TelegramNotifications,
  },
  PushoverNotifications: {
    title: 'Pushover',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/PushoverNotifications'),
    route: routes.PushoverNotifications,
    isHidden: !PUSHOVER_APP_TOKEN,
  },
  SlackNotifications: {
    title: 'Slack',
    isSubcategory: true,
    importComponent: () => import('@src/components/user-preferences/SlackNotifications'),
    route: routes.SlackNotifications,
    isHidden: !SLACK_CLIENT_ID,
  },
}
