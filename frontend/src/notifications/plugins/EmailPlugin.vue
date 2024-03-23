<template>
  <notification-channel-template
    ref="notificationChannelTemplate"
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <div class="row">
        <div class="col">
          <p class="text-muted mb-1">{{ $t("Notifications are sent to verified email addresses only.") }}</p>
          <p class="mb-4"><a href="/accounts/email">{{ $t("Manage email addresses") }}</a></p>
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
                id="id_account_notification_by_email"
                v-model="accountNotificationByEmail"
                type="checkbox"
                class="custom-control-input"
                :disabled="
                  $refs.notificationChannelTemplate
                    ? !$refs.notificationChannelTemplate.notificationsEnabled
                    : false
                "
              />
              <label class="custom-control-label" for="id_account_notification_by_email">
                <i18next :translation="$t('Account events {localizedDom}')">
                  <template #localizedDom>
                    <span class="text-muted setting-description"><br />{{$t("Plan changed; AI Detection Hours running low; etc.")}}</span>
                  </template>
                </i18next>

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
                <i18next :translation="$t('Account events {localizedDom}')">
                  <template #localizedDom>
                    <span class="text-muted setting-description"><br />{{$t("Plan changed; AI Detection Hours running low; etc.")}}</span>
                  </template>
                </i18next>
              </label>
            </div>
            <div class="setting-item-switch">
              <onoff-toggle
                v-model="accountNotificationByEmail"
                :theme="theme"
                :width="theme === 'ios' ? 48 : 30"
                :height="theme === 'ios' ? 24 : 12"
                :on-color="theme === 'ios' ? 'var(--color-primary)' : 'var(--color-primary-muted)'"
                off-color="var(--color-divider)"
                border-color="var(--color-divider)"
                :thumb-color="theme === 'ios' ? '#fff' : 'var(--color-primary)'"
                :disabled="
                  $refs.notificationChannelTemplate
                    ? !$refs.notificationChannelTemplate.notificationsEnabled
                    : false
                "
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
import { mobilePlatform } from '@src/lib/page-context'

export default {
  name: 'EmailPlugin',

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

  data() {
    return {
      accountNotificationByEmail: this.user.account_notification_by_email,
    }
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

  watch: {
    accountNotificationByEmail: function (newVal, prevVal) {
      this.$emit('updateNotificationChannel', {
        section: this.notificationChannel,
        propNames: [this.settingId],
        propValues: [newVal],
      })

      this.$emit('updateSetting', 'account_notification_by_email', newVal)
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
