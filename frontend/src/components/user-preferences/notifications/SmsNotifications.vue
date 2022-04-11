<template>
  <section v-if="notificationChannel.channelInfo">
    <h2 class="section-title">SMS</h2>

    <div v-if="twilioEnabled">
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

      <div>
        <div class="row">
          <div class="col">
            <h5 class="font-weight-bold">Alerts settings</h5>
          </div>
        </div>

        <notification-setting-switch
          class="mb-0"
          settingId="enabled"
          settingTitle="Enable"
          :errorMessages="errorMessages"
          :saving="saving"
          :notificationChannel="notificationChannel"
          @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
        />

        <div :class="{'inactive': !notificationsEnabled}">
          <hr class="my-1">
          <notification-setting-switch
            v-for="setting in notificationSettings"
            :key="setting.id"
            :settingId="setting.id"
            :settingTitle="setting.title"
            :settingDescription="setting.description"
            :isSubcategory="setting.isSubcategory"
            :disabled="!notificationsEnabled"
            :errorMessages="errorMessages"
            :saving="saving"
            :notificationChannel="notificationChannel"
            @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
          />
        </div>

      </div>
    </div>
    <div v-else>
      <p class="text-warning">Please configure the following variables in the "docker-compose.override.yml" file to enable SMS notifications:</p>
      <ul class="text-warning">
        <li>TWILIO_ACCOUNT_SID</li>
        <li>TWILIO_AUTH_TOKEN</li>
        <li>TWILIO_FROM_NUMBER</li>
      </ul>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NotificationSettingSwitch from '@src/components/user-preferences/notifications/NotificationSettingSwitch.vue'
import { getNotificationSettingKey } from '@src/lib/utils'

export default {
  name: 'SmsNotifications',

  components: {
    SavingAnimation,
    NotificationSettingSwitch,
  },

  props: {
    config: {
      default() {return {}},
      type: Object,
    },
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

  computed: {
    twilioEnabled() {
      const envVars = this.notificationChannel.pluginInfo ? (this.notificationChannel.pluginInfo.env_vars || {}) : {}
      for (const variable of Object.values(envVars)) {
        if (variable.is_required && !variable.is_set) {
          return false
        }
      }
      return true
    },
    notificationsEnabled() {
      return this.notificationChannel.channelInfo ? this.notificationChannel.channelInfo.enabled : false
    },
  },

  created() {
    if (!this.notificationChannel.channelInfo) {
      this.$emit('createNotificationChannel', this.notificationChannel.channelName)
    } else {
      if (this.notificationChannel.channelInfo.config) {
        this.phoneCountryCode = this.notificationChannel.channelInfo.config.phone_country_code
        this.phoneNumber = this.notificationChannel.channelInfo.config.phone_number
      }
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

      this.configUpdateTimeout = setTimeout(() => {
        this.notificationChannel.channelInfo.config = {
          phone_country_code: this.phoneCountryCode,
          phone_number: this.phoneNumber,
        }
        this.$emit('updateNotificationChannel', this.notificationChannel, ['config'])
      }, 1000)
    }
  },
}
</script>
