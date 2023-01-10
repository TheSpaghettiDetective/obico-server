<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    config-variable-title="Webhook URL"
    config-variable-placeholder="Discord Webhook"
    config-variable-name="webhook_url"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <small class="form-text text-muted">
        If you have a Discord channel you wish to receive notifications on, you can
        <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
          >generate webhook url</a
        >
        and enter it here.
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'DiscordPlugin',

  components: {
    NotificationChannelTemplate,
  },

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
      required: true,
    },
    notificationChannel: {
      type: Object,
      required: true,
    },
  },
}
</script>
