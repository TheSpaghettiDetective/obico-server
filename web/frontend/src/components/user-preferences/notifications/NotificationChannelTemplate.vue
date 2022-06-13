<template>
  <section>
    <h2 class="section-title">{{ notificationChannel.title }}</h2>

    <div v-if="envVarsToSet.length === 0">
      <slot name="header"></slot>

      <slot name="configuration">
        <div v-if="configVariableName" class="form-group row my-4">
          <label :for="`id_${settingKey(configVariableName)}`" class="col-12 col-form-label">{{ configVariableTitle }}</label>
          <div class="col-12 col-form-label">
            <saving-animation :errors="errorMessages[settingKey('config')]" :saving="saving[settingKey('config')]">
              <input
                type="text"
                :placeholder="configVariablePlaceholder"
                class="form-control"
                :id="`id_${settingKey(configVariableName)}`"
                v-model="configVariable"
              >
            </saving-animation>
          </div>
        </div>
      </slot>

      <div v-if="channelCreated && showSettings">
        <notification-setting-switch
          settingId="enabled"
          settingTitle="Enable notification"
          :isHeader="true"
          :errorMessages="errorMessages"
          :saving="saving"
          :notificationChannel="notificationChannel"
          :bottomDivider="true"
          @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
        />
        <div :class="{'inactive': !notificationsEnabled}">
          <slot name="custom-settings"></slot>
          <div
            v-for="setting in notificationSettings"
            :key="setting.id"
          >
            <template v-if="setting.id === 'printer_status_change'">
              <!-- FIXME: reuse NotificationSettingSwitch -->
              <div v-if="theme === 'web'" class="row">
                <div class="col-12 col-form-label">
                  <saving-animation :errors="[]" :saving="false">
                    <div class="custom-control custom-checkbox form-check-inline">
                      <input
                        type="checkbox"
                        class="custom-control-input"
                        :id="`id_${settingKey(setting.id)}`"
                        :disabled="!notificationsEnabled"
                        v-model="printerStatusChangeNotifications"
                      >
                      <label class="custom-control-label" :for="`id_${settingKey(setting.id)}`">
                        {{ setting.title }}
                        <span  v-if="setting.description" class="text-muted setting-description"><br>{{ setting.description }}</span>
                      </label>
                    </div>
                  </saving-animation>
                </div>
              </div>
              <div v-else>
                <saving-animation :errors="[]" :saving="false">
                  <div class="mobile-setting-item-wrapper">
                    <div class="setting-item-text">
                      <label :for="`id_${settingKey(setting.id)}`">
                        {{ setting.title }}
                        <span v-if="setting.description" class="text-muted setting-description"><br>{{ setting.description }}</span>
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
                        v-model="printerStatusChangeNotifications"
                        :disabled="!notificationsEnabled"
                        class="mb-0"
                      />
                    </div>
                  </div>
                </saving-animation>
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

      <slot name="footer"></slot>
    </div>
    <div v-else>
      <p class="text-warning">Please configure the following variables in the ".env" file:</p>
      <ul class="text-warning">
        <li v-for="variable in envVarsToSet" :key="variable">{{ variable }}</li>
      </ul>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NotificationSettingSwitch from '@src/components/user-preferences/notifications/NotificationSettingSwitch.vue'
import { getNotificationSettingKey } from '@src/lib/utils'
import defaultNotificationSettings from '@config/user-preferences/notification-settings'
import { mobilePlatform } from '@src/lib/page_context'

export default {
  name: 'NotificationChannelTemplate',

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
    notificationChannel: {
      type: Object,
      required: true,
    },
    notificationSettings: {
      type: Array,
      default: () => defaultNotificationSettings,
    },
    showSettings: {
      type: Boolean,
      default: true,
    },
    configVariableTitle: {
      type: String,
    },
    configVariablePlaceholder: {
      type: String,
    },
    configVariableName: {
      type: String,
    }
  },

  data() {
    return {
      configVariable: null,
      configUpdateTimeout: null,
    }
  },

  computed: {
    channelCreated() {
      return !!this.notificationChannel.channelInfo
    },
    notificationsEnabled() {
      return this.notificationChannel.channelInfo ? this.notificationChannel.channelInfo.enabled : false
    },
    envVarsToSet() {
      const envVars = this.notificationChannel.pluginInfo?.env_vars || {}
      let missedEnvVars = []
      for (const [key, val] of Object.entries(envVars)) {
        if (val.is_required && !val.is_set) {
          missedEnvVars.push(key)
        }
      }
      return missedEnvVars
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

  created() {
    if (this.notificationChannel.channelInfo && this.notificationChannel.channelInfo.config && this.configVariableName) {
      this.configVariable = this.notificationChannel.channelInfo.config[this.configVariableName]
    } else {
      this.configVariable = ''
    }
  },

  watch: {
    configVariable(newValue, oldValue) {
      if (oldValue === null) {
        return
      }
      this.$emit('clearErrorMessages', this.settingKey('config'))
      this.updateConfig()
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
        [this.configVariableName]: this.configVariable,
      }

      if (this.channelCreated) {
        this.configUpdateTimeout = setTimeout(() => {
          if (this.configVariable) {
            this.notificationChannel.channelInfo.config = config
            this.$emit('updateNotificationChannel', this.notificationChannel, ['config'])
          } else {
            this.$emit('deleteNotificationChannel', this.notificationChannel)
          }
        }, 1000)
      } else if (this.configVariable) {
        this.configUpdateTimeout = setTimeout(() => this.$emit('createNotificationChannel', this.notificationChannel, config), 1000)
      }
    }
  }
}
</script>

<style lang="sass" scoped>
.setting-description
  font-size: 14px
  margin-bottom: 0

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
