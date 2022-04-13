<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    configVariableTitle="Access Token"
    configVariablePlaceholder="Pushbullet Access Token"
    configVariableName="access_token"

    @createNotificationChannel="(channel) => $emit('createNotificationChannel', channel)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
  >
    <template #header>
      <small class="form-text text-muted">
        If you have a Pushbullet account, you can
        <a href="https://www.pushbullet.com/#settings" target="_blank">generate an access token</a>
        and enter it here.
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'pushbullet',

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
