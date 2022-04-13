<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    configVariableTitle="Webhook URL"
    configVariablePlaceholder="Discord Webhook"
    configVariableName="webhook_url"

    @createNotificationChannel="(channel) => $emit('createNotificationChannel', channel)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
  >
    <template #header>
      <small class="form-text text-muted">
        If you have a Discord channel you wish to receive notifications on, you can
        <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks">generate webhook url</a>
        and enter it here.
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'discord',

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
