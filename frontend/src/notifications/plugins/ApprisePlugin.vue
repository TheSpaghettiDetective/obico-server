<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    :configVariableTitle="$t('Apprise URL')"
    :configVariablePlaceholder="$t('e.g. ntfy://user:pass@ntfy.sh/obico')"
    configVariableName="apprise_url"

    @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <small class="form-text text-muted">
        <i18next :translation="$t('Send notifications through Apprise. Enter an Apprise URL for your service and see the {localizedDom} for the URL format.')">
          <template #localizedDom>
            <a href="https://github.com/caronc/apprise/wiki" target="_blank">{{$t("Apprise wiki")}}</a>
          </template>
        </i18next>
      </small>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'ApprisePlugin',

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
