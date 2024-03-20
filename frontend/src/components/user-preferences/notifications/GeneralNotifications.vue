<template>
  <section class="notifications">
    <h2 class="section-title">{{ $t("Notifications") }}</h2>

    <!-- FIXME: reuse NotificationSettingSwitch -->
    <div v-if="theme === 'web'" class="row">
      <div class="col-12 col-form-label">
        <saving-animation
          :errors="errorMessages.notification_enabled"
          :saving="saving.notification_enabled"
        >
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              id="id_notification_enabled"
              v-model="notificationsEnabled"
              type="checkbox"
              class="custom-control-input"
            />
            <label class="custom-control-label" for="id_notification_enabled">
              {{$t("Enable notifications")}}
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
    <div v-else>
      <saving-animation
        :errors="errorMessages.notification_enabled"
        :saving="saving.notification_enabled"
      >
        <div class="mobile-setting-item-wrapper">
          <div class="setting-item-text">
            <label for="id_notification_enabled">{{ $t("Enable notifications") }}</label>
          </div>
          <div class="setting-item-switch">
            <onoff-toggle
              v-model="notificationsEnabled"
              :theme="theme"
              :width="theme === 'ios' ? 48 : 30"
              :height="theme === 'ios' ? 24 : 12"
              :on-color="theme === 'ios' ? 'var(--color-primary)' : 'var(--color-primary-muted)'"
              off-color="var(--color-divider)"
              border-color="var(--color-divider)"
              :thumb-color="theme === 'ios' ? '#fff' : 'var(--color-primary)'"
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
import { mobilePlatform } from '@src/lib/page-context'

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

  data() {
    return {
      notificationsEnabled: this.user.notification_enabled,
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
    notificationsEnabled: function (newVal, prevVal) {
      this.$emit('updateSetting', 'notification_enabled', newVal)
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
