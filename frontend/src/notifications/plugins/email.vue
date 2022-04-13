<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"

    @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"

    ref="notificationChannelTemplate"
  >
    <template #header>
      <div class="row">
        <div class="col">
          <p class="text-muted mb-1">Notifications are sent to verified email addresses only.</p>
          <p class="mb-4"><a href="/accounts/email">Manage email addresses</a></p>
        </div>
      </div>
    </template>

    <template #custom-settings>
      <div class="row">
        <div class="col col-form-label">
          <saving-animation :errors="errorMessages['account_notification_by_email']" :saving="saving['account_notification_by_email']">
            <div class="custom-control custom-checkbox form-check-inline">
              <input
                type="checkbox"
                class="custom-control-input"
                id="id_account_notification_by_email"
                :disabled="$refs.notificationChannelTemplate ? !$refs.notificationChannelTemplate.notificationsEnabled : false"
                v-model="user.account_notification_by_email"
                @change="$emit('updateSetting', 'account_notification_by_email')"
              >
              <label class="custom-control-label" for="id_account_notification_by_email">
                Account events
                <span class="text-muted setting-description"><br>Plan changed; Detective Hours running low; etc.</span>
              </label>
            </div>
          </saving-animation>
        </div>
      </div>
    </template>
  </notification-channel-template>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'

export default {
  name: 'email',

  components: {
    SavingAnimation,
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
    user: {
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
