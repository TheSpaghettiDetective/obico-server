<template>
  <div v-if="theme === 'web'" class="row">
    <div class="col-12 col-form-label" :class="{ 'pl-5': isSubcategory }">
      <saving-animation
        :errors="errorMessages ? errorMessages[settingKey(settingId)] : []"
        :saving="saving ? saving[settingKey(settingId)] : false"
      >
        <div class="custom-control custom-checkbox form-check-inline">
          <input
            :id="`id_${settingKey(settingId)}`"
            v-model="value"
            type="checkbox"
            class="custom-control-input"
            :disabled="disabled"
          />
          <label :class="['custom-control-label', labelClass]" :for="`id_${settingKey(settingId)}`">
            {{ settingTitle }}
            <span v-if="settingDescription" class="text-muted setting-description"
              ><br />{{ settingDescription }}</span
            >
          </label>
        </div>
      </saving-animation>
    </div>
    <div v-if="bottomDivider" class="col-12">
      <hr class="my-1" />
    </div>
  </div>
  <div v-else>
    <saving-animation
      :errors="errorMessages ? errorMessages[settingKey(settingId)] : []"
      :saving="saving ? saving[settingKey(settingId)] : false"
    >
      <div class="mobile-setting-item-wrapper" :class="{ 'is-subcategory': isSubcategory }">
        <div class="setting-item-text">
          <label :class="labelClass" :for="`id_${settingKey(settingId)}`">
            {{ settingTitle }}
            <span v-if="settingDescription" class="text-muted setting-description"
              ><br />{{ settingDescription }}</span
            >
          </label>
        </div>
        <div class="setting-item-switch">
          <onoff-toggle
            v-model="value"
            :theme="theme"
            :width="theme === 'ios' ? 48 : 30"
            :height="theme === 'ios' ? 24 : 12"
            :on-color="theme === 'ios' ? 'var(--color-primary)' : 'var(--color-primary-muted)'"
            off-color="var(--color-divider)"
            border-color="var(--color-divider)"
            :thumb-color="theme === 'ios' ? '#fff' : 'var(--color-primary)'"
            :disabled="disabled"
            class="mb-0"
          />
        </div>
      </div>
    </saving-animation>
  </div>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import { getNotificationSettingKey } from '@src/lib/utils'
import { mobilePlatform } from '@src/lib/page-context'

export default {
  name: 'NotificationSettingSwitch',

  components: {
    SavingAnimation,
  },

  props: {
    errorMessages: {
      type: Object || null,
      default: null,
    },
    saving: {
      type: Object || null,
      default: null,
    },
    notificationChannel: {
      type: Object,
      required: true,
    },
    settingId: {
      type: String,
      required: true,
    },
    settingTitle: {
      type: String,
      required: true,
    },
    settingDescription: {
      type: String,
      default: '',
    },
    isSubcategory: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    bottomDivider: {
      type: Boolean,
      default: false,
    },
    isHeader: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      value: this.notificationChannel.channelInfo[this.settingId],
    }
  },

  computed: {
    theme() {
      const platform = mobilePlatform()
      if (!platform) {
        return 'web'
      } else {
        return platform === 'ios' ? 'ios' : 'material'
      }
    },
    labelClass() {
      return this.isHeader ? 'lg' : ''
    },
  },

  watch: {
    value: function (newVal, prevVal) {
      this.$emit('updateNotificationChannel', {
        section: this.notificationChannel,
        propNames: [this.settingId],
        propValues: [newVal],
      })
    },
  },

  methods: {
    settingKey(settingId) {
      return getNotificationSettingKey(this.notificationChannel, settingId)
    },
  },
}
</script>

<style lang="sass" scoped>
.setting-description
  font-size: 14px
  margin-bottom: 0
.form-check-inline
  label
    &.lg
      font-size: 1.15em
      font-weight: bolder
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
    &.lg
      font-size: 1.15em
      font-weight: bolder
</style>
