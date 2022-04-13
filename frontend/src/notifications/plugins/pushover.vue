<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    configVariableTitle="User Key"
    configVariablePlaceholder="Pushover User Key"
    configVariableName="user_key"

    @createNotificationChannel="(channel) => $emit('createNotificationChannel', channel)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
  >
    <template #header>
      <small class="form-text text-muted">
        If you have a Pushover account, you can
        <a href="https://support.pushover.net/i7-what-is-pushover-and-how-do-i-use-it" target="_blank">get your User Key</a>
        and enter it here.
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'pushover',

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
