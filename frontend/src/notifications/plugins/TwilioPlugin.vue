<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    :notification-settings="notificationSettings"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #configuration>
      <div class="form-group row">
        <label for="id_email" class="col-12 col-form-label">{{ $t("Phone Number") }}</label>
        <div class="col-12 col-form-label">
          <saving-animation
            :errors="errorMessages[settingKey('config')]"
            :saving="saving[settingKey('config')]"
          >
            <div class="form-group form-row">
              <div class="col-sm-6 col-md-4 mb-2 mb-sm-0">
                <input
                  id="id_phone_code"
                  v-model="phoneCountryCode"
                  type="text"
                  class="form-control"
                  :placeholder="$t('Country Code')"
                />
              </div>
              <div class="col-sm-6 col-md-8">
                <input
                  id="id_phone_number"
                  v-model="phoneNumber"
                  type="text"
                  class="form-control"
                  :placeholder="$t('Phone Number')"
                />
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
  name: 'TwilioPlugin',

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
      default() {
        return {}
      },
      type: Object,
    },
  },

  data() {
    return {
      notificationSettings: [
        {
          id: 'notify_on_failure_alert',
          title: `${this.$i18next.t('Failure alerts')}`,
          description: `${this.$i18next.t('When possible failures are detected')}`,
        },
      ],
      configUpdateTimeout: null,
      phoneCountryCode: null,
      phoneNumber: null,
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

      if (
        this.config.twilioCountryCodes &&
        this.config.twilioCountryCodes.length !== 0 &&
        !this.config.twilioCountryCodes.includes(codeNumber)
      ) {
        this.$emit(
          'addErrorMessage',
          this.settingKey('config'),
          `${this.$i18next.t("Oops, we don't send SMS to this country code")}`
        )
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

  created() {
    if (this.notificationChannel.channelInfo && this.notificationChannel.channelInfo.config) {
      this.phoneCountryCode = this.notificationChannel.channelInfo.config.phone_country_code
      this.phoneNumber = this.notificationChannel.channelInfo.config.phone_number
    }
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
          this.$emit('updateNotificationChannel', {
            section: this.notificationChannel,
            propNames: ['config'],
            propValues: [config],
          })
        }, 1000)
      } else {
        this.configUpdateTimeout = setTimeout(() => {
          this.$emit('createNotificationChannel', {
            section: this.notificationChannel,
            config,
            opts: {
              notify_on_print_done: 'f',
              notify_on_print_cancelled: 'f',
              notify_on_filament_change: 'f',
              notify_on_heater_status: 'f',
              notify_on_print_start: 'f',
              notify_on_print_pause: 'f',
              notify_on_print_resume: 'f'
            },
          })
        }, 1000)
      }
    },
  },
}
</script>
