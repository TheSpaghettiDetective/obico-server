<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"
    :notificationSettings="notificationSettings"

    @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #configuration>
      <div class="form-group row">
        <label for="id_email" class="col-12 col-form-label">Phone Number</label>
        <div class="col-12 col-form-label">
          <saving-animation :errors="errorMessages[settingKey('config')]" :saving="saving[settingKey('config')]">
            <div class="form-group form-row">
              <div class="col-sm-6 col-md-4 mb-2 mb-sm-0">
                <input
                  type="text"
                  class="form-control"
                  id="id_phone_code"
                  placeholder="Country Code"
                  v-model="phoneCountryCode"
                >
              </div>
              <div class="col-sm-6 col-md-8">
                <input
                  type="text"
                  class="form-control"
                  id="id_phone_number"
                  placeholder="Phone Number"
                  v-model="phoneNumber"
                >
              </div>
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
import { getNotificationSettingKey } from '@src/lib/utils'

export default {
  name: 'twilio',

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
    config: {
      default() {return {}},
      type: Object,
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
      ],
      configUpdateTimeout: null,
      phoneCountryCode: null,
      phoneNumber: null,
    }
  },

  created() {
    if (this.notificationChannel.channelInfo && this.notificationChannel.channelInfo.config) {
      this.phoneCountryCode = this.notificationChannel.channelInfo.config.phone_country_code
      this.phoneNumber = this.notificationChannel.channelInfo.config.phone_number
    }
  },

  watch: {
    phoneCountryCode(newValue, oldValue) {
      if (oldValue === null) {
        return
      }

      this.$emit('clearErrorMessages', this.settingKey('config'))

      // Allow clear data
      if (newValue === '') {
        if (this.phoneNumber === '') {
          this.updateConfig()
        }
        return
      }

      const codeNumber = parseInt(newValue.replace(/\s/g, '')) // will parse both '1' / '+1', clear spaces for safety
      if (isNaN(codeNumber)) {
        return
      }

      if (this.config.twilioCountryCodes && (this.config.twilioCountryCodes.length !== 0) && !this.config.twilioCountryCodes.includes(codeNumber)) {
        this.$emit('addErrorMessage', this.settingKey('config'), 'Oops, we don\'t send SMS to this country code')
      } else {
        if (this.phoneNumber) {
          this.updateConfig()
        }
      }
    },
    phoneNumber(newValue, oldValue) {
      if (oldValue === null) {
        return
      }

      this.$emit('clearErrorMessages', this.settingKey('config'))

      // Allow clear data
      if (newValue === '') {
        if (this.phoneCountryCode === '') {
          this.updateConfig()
        }
        return
      }

      if (this.phoneCountryCode) {
        this.updateConfig()
      }
    },
  },

  methods: {
    settingKey(settingId) {
      return getNotificationSettingKey(this.notificationChannel, settingId)
    },
    updateConfig() {
      if (this.configUpdateTimeout) {
        clearTimeout(this.configUpdateTimeout)
      }

      const config = {
        phone_country_code: this.phoneCountryCode,
        phone_number: this.phoneNumber,
      }

      if (this.notificationChannel.channelInfo) {
        this.configUpdateTimeout = setTimeout(() => {
          this.notificationChannel.channelInfo.config = config
          this.$emit('updateNotificationChannel', this.notificationChannel, ['config'])
        }, 1000)
      } else {
        this.configUpdateTimeout = setTimeout(() => this.$emit('createNotificationChannel', this.notificationChannel, config), 1000)
      }
    }
  },
}
</script>
