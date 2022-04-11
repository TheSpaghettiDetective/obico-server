<template>
  <div class="row">
    <div class="col col-form-label" :class="{'pl-5': isSubcategory}">
      <saving-animation :errors="errorMessages[settingKey(settingId)]" :saving="saving[settingKey(settingId)]">
        <div class="custom-control custom-checkbox form-check-inline">
          <input
            type="checkbox"
            class="custom-control-input"
            :id="`id_${settingKey(settingId)}`"
            :disabled="disabled"
            v-model="notificationChannel.channelInfo[settingId]"
            @change="$emit('updateNotificationChannel', notificationChannel, [settingId])"
          >
          <label class="custom-control-label" :for="`id_${settingKey(settingId)}`">
            {{ settingTitle }}
            <span v-if="settingDescription" class="text-muted setting-description"><br>{{ settingDescription }}</span>
          </label>

        </div>
      </saving-animation>
    </div>
  </div>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import { getNotificationSettingKey } from '@src/lib/utils'

export default {
  name: 'NotificationSettingSwitch',

  components: {
    SavingAnimation,
  },

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
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
    },
    isSubcategory: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    settingKey(settingId) {
      return getNotificationSettingKey(this.notificationChannel, settingId)
    }
  },
}
</script>

<style lang="sass" scoped>
.setting-description
  font-size: 14px
  margin-bottom: 0
</style>
