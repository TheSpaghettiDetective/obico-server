<template>
  <section v-if="notificationChannel.channelInfo">
    <h2 class="section-title">Email</h2>
    <div class="row">
      <div class="col">
        <p class="text-muted mb-1">Notifications are sent to verified email addresses only.</p>
        <p class="mb-4"><a href="/accounts/email">Manage email addresses</a></p>
      </div>
    </div>

    <div>
      <div class="row">
        <div class="col">
          <h5 class="font-weight-bold">Alerts settings</h5>
        </div>
      </div>

      <notification-setting-switch
        settingId="enabled"
        settingTitle="Enable"
        :errorMessages="errorMessages"
        :saving="saving"
        :notificationChannel="notificationChannel"
        @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
      />

      <div :class="{'inactive': !notificationsEnabled}">
        <hr class="my-1">
        <div class="row">
          <div class="col col-form-label">
            <saving-animation :errors="errorMessages['account_notification_by_email']" :saving="saving['account_notification_by_email']">
              <div class="custom-control custom-checkbox form-check-inline">
                <input
                  type="checkbox"
                  class="custom-control-input"
                  id="id_account_notification_by_email"
                  :disabled="!notificationsEnabled"
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

        <div
          v-for="setting in notificationSettings"
          :key="setting.id"
        >
          <template v-if="setting.id === 'printer_status_change'">
            <div class="row">
              <div class="col col-form-label">
                <saving-animation :errors="[]" :saving="false">
                  <div class="custom-control custom-checkbox form-check-inline">
                    <input
                      type="checkbox"
                      class="custom-control-input"
                      :id="`id_${notificationChannel.channelName}_printer_status_change`"
                      :disabled="!notificationsEnabled"
                      v-model="printerStatusChangeNotifications"
                    >
                    <label class="custom-control-label" :for="`id_${notificationChannel.channelName}_printer_status_change`">
                      {{ setting.title }}
                      <span v-if="setting.description" class="text-muted setting-description"><br>{{ setting.description }}</span>
                    </label>
                  </div>
                </saving-animation>
              </div>
            </div>
          </template>
          <template v-else>
            <notification-setting-switch
              :settingId="setting.id"
              :settingTitle="setting.title"
              :settingDescription="setting.description"
              :disabled="!notificationsEnabled"
              :errorMessages="errorMessages"
              :saving="saving"
              :notificationChannel="notificationChannel"
              @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
            />
          </template>
          <div v-if="setting.subcategories">
            <notification-setting-switch
              v-for="subcategory in setting.subcategories"
              :key="subcategory.id"
              :settingId="subcategory.id"
              :settingTitle="subcategory.title"
              :settingDescription="subcategory.description"
              :isSubcategory="true"
              :disabled="!notificationsEnabled"
              :errorMessages="errorMessages"
              :saving="saving"
              :notificationChannel="notificationChannel"
              @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NotificationSettingSwitch from '@src/components/user-preferences/notifications/NotificationSettingSwitch.vue'
import { getNotificationSettingKey } from '@src/lib/utils'

export default {
  name: 'EmailNotifications',

  components: {
    SavingAnimation,
    NotificationSettingSwitch,
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
      notificationSettings: [
        {
          id: 'notify_on_failure_alert',
          title: 'Failure alerts',
          description: 'When possible failures are detected',
        },
        {
          id: 'printer_status_change',
          title: 'Printer status change',
          subcategories: [
            {
              id: 'notify_on_print_done',
              title: 'When print is done',
              enabledByDefault: true,
            },
            {
              id: 'notify_on_print_cancelled',
              title: 'When print is cancelled',
              enabledByDefault: false,
            },
            {
              id: 'notify_on_filament_change',
              title: 'When filament runs out or needs a change',
              enabledByDefault: true,
            },
            {
              id: 'notify_on_other_print_events',
              title: 'When other event happens',
              description: 'Print start, pause, resume, etc. (TBD. Help wanted!)',
              enabledByDefault: false,
            },
          ]
        },
        {
          id: 'notify_on_heater_status',
          title: 'Heater status change',
          description: 'Reached target or cooled down (TBD. Help wanted!)',
        },
      ]
    }
  },

  computed: {
    notificationsEnabled() {
      return this.notificationChannel.channelInfo ? this.notificationChannel.channelInfo.enabled : false
    },
    printerStatusChangeNotifications: {
      get: function() {
        if (!this.notificationChannel.channelInfo) {
          return null
        }
        const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
        for (const subcategory of subcategories) {
          if (this.notificationChannel.channelInfo[subcategory.id]) {
            return true
          }
        }
        return false
      },
      set: function(newValue) {
        if (newValue) {
          const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
          let changedProps = []
          for (const subcategory of subcategories) {
            if (subcategory.enabledByDefault) {
              this.notificationChannel.channelInfo[subcategory.id] = true
              changedProps.push(subcategory.id)
            }
          }
          if (changedProps.length) {
            this.$emit('updateNotificationChannel', this.notificationChannel, changedProps)
          }
        } else {
          const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
          let changedProps = []
          for (const subcategory of subcategories) {
            if (this.notificationChannel.channelInfo[subcategory.id]) {
              this.notificationChannel.channelInfo[subcategory.id] = false
              changedProps.push(subcategory.id)
            }
          }
          if (changedProps.length) {
            this.$emit('updateNotificationChannel', this.notificationChannel, changedProps)
          }
        }
      }
    },
  },

  created() {
    if (!this.notificationChannel.channelInfo) {
      this.$emit('createNotificationChannel', this.notificationChannel.channelName)
    }
  },

  methods: {
    settingKey(settingId) {
      return getNotificationSettingKey(this.notificationChannel, settingId)
    },
  }
}
</script>

<style lang="sass" scoped>
.setting-description
  font-size: 14px
  margin-bottom: 0
</style>
