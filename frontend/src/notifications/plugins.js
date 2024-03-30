import i18n from '@src/i18n/i18n.js'

export default {
  email: {
    displayName: `${i18n.t('Email')}`,
    componentName: 'EmailPlugin',
  },
  twilio: {
    displayName: `${i18n.t('SMS')}`,
    componentName: 'TwilioPlugin',
  },
  pushbullet: {
    displayName: `${i18n.t('Pushbullet')}`,
    componentName: 'PushbulletPlugin',
  },
  discord: {
    displayName: `${i18n.t('Discord')}`,
    componentName: 'DiscordPlugin',
  },
  telegram: {
    displayName: `${i18n.t('Telegram')}`,
    componentName: 'TelegramPlugin',
  },
  pushover: {
    displayName: `${i18n.t('Pushover')}`,
    componentName: 'PushoverPlugin',
  },
  slack: {
    displayName: `${i18n.t('Slack')}`,
    componentName: 'SlackPlugin',
  },
  webhook: {
    displayName: `${i18n.t('Webhook')}`,
    componentName: 'WebhookPlugin',
  },
}
