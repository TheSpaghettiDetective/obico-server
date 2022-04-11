<template>
  <section class="notifications">
    <h2 class="section-title">Notifications</h2>
    <div class="row">
      <div class="col col-form-label">
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
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'


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
}
</script>
