<template>
  <section class="notifications">
    <h2 class="section-title">Notifications</h2>

    <!-- FIXME: reuse NotificationSettingSwitch -->
    <div v-if="theme === 'web'" class="row">
      <div class="col-12 col-form-label">
        <saving-animation :errors="errorMessages.notification_enabled" :saving="saving.notification_enabled">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_notification_enabled"
              v-model="user.notification_enabled"
              @change="$emit('updateSetting', 'notification_enabled')"
            >
            <label class="custom-control-label" for="id_notification_enabled">
              Enable notifications
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
    <div v-else>
      <saving-animation :errors="errorMessages.notification_enabled" :saving="saving.notification_enabled">
        <div class="mobile-setting-item-wrapper">
          <div class="setting-item-text">
            <label for="id_notification_enabled">
              Enable notifications
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
              v-model="user.notification_enabled"
              @input="$emit('updateSetting', 'notification_enabled')"
              class="mb-0"
            />
          </div>
        </div>
      </saving-animation>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import { mobilePlatform } from '@src/lib/page_context'

export default {
  name: 'GeneralNotifications',

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
      required: true,
    },
    user: {
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
