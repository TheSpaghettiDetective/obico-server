<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    :configVariableTitle="$t('Webhook URL')"
    :configVariablePlaceholder="$t('Custom Webhook URL')"
    configVariableName="custom_webhook_URL"

    @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <small class="form-text text-muted">
        {{$t("Enter a custom webhook URL at which to receive notifications.")}} 
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'WebhookPlugin',

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
