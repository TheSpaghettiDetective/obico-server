<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    config-variable-title="Access Token"
    config-variable-placeholder="Pushbullet Access Token"
    config-variable-name="access_token"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
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
  name: 'PushbulletPlugin',

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
