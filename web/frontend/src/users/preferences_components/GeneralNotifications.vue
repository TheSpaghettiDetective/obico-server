<template>
  <section class="notifications">
    <h2 class="section-title">Notifications</h2>
    <div class="row">
      <div class="col col-form-label">
        <saving-animation :errors="errorMessages.notify_on_done" :saving="saving.notify_on_done">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_notify_on_done"
              v-model="user.notify_on_done"
              @change="$emit('updateSetting', 'notify_on_done')"
            >
            <label class="custom-control-label" for="id_notify_on_done">
              Notify me when print job is done
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
    <div class="row">
      <div class="col col-form-label">
        <saving-animation :errors="errorMessages.notify_on_canceled" :saving="saving.notify_on_canceled">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_notify_on_canceled"
              v-model="user.notify_on_canceled"
              @change="$emit('updateSetting', 'notify_on_canceled')"
            >
            <label class="custom-control-label" for="id_notify_on_canceled">
              Notify me when print job is cancelled
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
    <div class="row">
      <div class="col col-form-label">
        <saving-animation :errors="errorMessages.notify_on_filament_change_req" :saving="saving.notify_on_filament_change_req">
          <div class="custom-control custom-checkbox form-check-inline" style="display: inline-flex; gap: 6px;">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_notify_on_filament_change_req"
              v-model="user.notify_on_filament_change_req"
              @change="$emit('updateSetting', 'notify_on_filament_change_req')"
            >
            <label class="custom-control-label" for="id_notify_on_filament_change_req">
              Notify me when filament runs out or needs a change
            </label>
            <help-widget class="mt-1" id="filament-change-on-notification-preferences"></help-widget>
          </div>
        </saving-animation>
      </div>
    </div>
    <div class="row">
      <div class="col col-form-label">
        <saving-animation :errors="errorMessages.account_notification_by_email" :saving="saving.account_notification_by_email">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_account_notification_by_email"
              v-model="user.account_notification_by_email"
              @change="$emit('updateSetting', 'account_notification_by_email')"
            >
            <label class="custom-control-label" for="id_account_notification_by_email">
              Notify me on account events (such as running out of Detective Hours)
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@common/SavingAnimation.vue'
import HelpWidget from '@common/HelpWidget.vue'

export default {
  name: 'GeneralNotifications',

  components: {
    SavingAnimation,
    HelpWidget,
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
}
</script>
