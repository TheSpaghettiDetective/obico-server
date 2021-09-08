<template>
  <section class="email">
    <h2 class="section-title">Email</h2>
    <div class="row">
      <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Primary Email</label>
      <div class="col-md-10 col-sm-9 col-form-label text-muted">{{user.email}} ({{user.is_primary_email_verified ? 'Verified' : 'Unverified'}})
        <div class="form-text"><a href="/accounts/email">Manage email addresses</a></div>
      </div>
    </div>
    <div class="row">
      <label class="col-md-2 col-sm-3 col-form-label"></label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <saving-animation :errors="errorMessages.alert_by_email" :saving="saving.alert_by_email">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_alert_by_email"
              v-model="user.alert_by_email"
              @change="$emit('updateSetting', 'alert_by_email')"
            >
            <label class="custom-control-label" for="id_alert_by_email">
              Send failure alerts to all verified email addresses
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
    <div class="row">
      <label class="col-md-2 col-sm-3 col-form-label"></label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <saving-animation :errors="errorMessages.print_notification_by_email" :saving="saving.print_notification_by_email">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_print_notification_by_email"
              v-model="user.print_notification_by_email"
              @change="$emit('updateSetting', 'print_notification_by_email')"
            >
            <label class="custom-control-label" for="id_print_notification_by_email">
              Send print job notifications to all verified email addresses
            </label>
          </div>
        </saving-animation>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@common/SavingAnimation.vue'

export default {
  name: 'EmailPreferences',

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