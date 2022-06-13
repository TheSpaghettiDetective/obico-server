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
      <!-- FIXME: reuse NotificationSettingSwitch -->
      <div v-if="theme === 'web'" class="row">
        <div class="col-12 col-form-label">
          <saving-animation :errors="[]" :saving="false">
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
                <span class="text-muted setting-description"><br>Plan changed; AI Detection Hours running low; etc.</span>
              </label>
            </div>
          </saving-animation>
        </div>
      </div>
      <div v-else>
        <saving-animation :errors="[]" :saving="false">
          <div class="mobile-setting-item-wrapper">
            <div class="setting-item-text">
              <label for="id_account_notification_by_email">
                Account events
                <span class="text-muted setting-description"><br>Plan changed; AI Detection Hours running low; etc.</span>
              </label>
            </div>
            <div class="setting-item-switch">
              <onoff-toggle
                :theme="theme"
                :width="theme === 'ios' ? 48 : 30"
                :height="theme === 'ios' ? 24 : 12"
                :onColor="theme === 'ios' ? 'var(--color-primary)' : 'var(--color-on-primary)'"
                offColor="var(--color-divider)"
                borderColor="var(--color-divider)"
                :thumbColor="theme === 'ios' ? 'var(--color-on-primary)' : 'var(--color-primary)'"
                v-model="user.account_notification_by_email"
                @input="$emit('updateSetting', 'account_notification_by_email')"
                :disabled="$refs.notificationChannelTemplate ? !$refs.notificationChannelTemplate.notificationsEnabled : false"
                class="mb-0"
              />
            </div>
          </div>
        </saving-animation>
      </div>
    </template>
  </notification-channel-template>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'
import { mobilePlatform } from '@src/lib/page_context'

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

  computed: {
    // FIXME: remove after NotificationSettingSwitch reuse
    theme() {
      const platform = mobilePlatform()
      if (!platform) {
        return 'web'
      } else {
        return platform === 'ios' ? 'ios' : 'material'
      }
    },
  },
}
</script>

<style lang="sass" scoped>
// FIXME: remove after NotificationSettingSwitch reuse
.setting-description
  font-size: 14px
  margin-bottom: 0
.mobile-setting-item-wrapper
  display: flex
  align-items: center
  gap: .5rem
  padding: 10px 0
  border-bottom: 1px solid var(--color-divider)
  &.is-subcategory
    margin-left: 1rem
  .setting-item-text
    flex: 1
  .setting-item-switch
    flex: 0 0 1
  label
    margin-bottom: 0
</style>
