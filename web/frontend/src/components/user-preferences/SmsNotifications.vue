<template>
  <section class="sms">
    <h2 class="section-title">SMS</h2>
    <div class="form-group row">
      <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Phone Number</label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <div v-if="twilioEnabled">
          <saving-animation :errors="errorMessages.phone" :saving="saving.phone">
            <div class="form-group form-row">
              <div class="col-sm-6 col-md-4">
                <input
                  type="text"
                  class="form-control"
                  id="id_phone_code"
                  placeholder="Country Code"
                  v-model="user.phone_country_code"
                >
              </div>
              <div class="col-sm-6 col-md-8">
                <input
                  type="text"
                  class="form-control"
                  id="id_phone_number"
                  placeholder="Phone Number"
                  v-model="user.phone_number"
                >
              </div>
            </div>
          </saving-animation>
        </div>
        <p v-else class="text-muted">Please configure TWILIO_* items in settings to enable phone alert.</p>
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.alert_by_sms" :saving="saving.alert_by_sms">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_alert_by_sms"
              v-model="user.alert_by_sms"
              @change="$emit('updateSetting', 'alert_by_sms')"
            >
            <label class="custom-control-label" for="id_alert_by_sms">
              Alert me via SMS when print failures are detected
            </label>
          </div>
        </saving-animation>
        <small v-if="!user.is_pro" class="text-warning">Note: You won't be alerted via SMS because this is a Pro feature and you are on the Free plan.</small>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'
import { settings } from '@src/lib/page_context'

export default {
  name: 'SmsNotifications',

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
      twilioEnabled: false,
    }
  },

  created() {
    const {TWILIO_ENABLED} = settings()
    this.twilioEnabled = !!TWILIO_ENABLED
  },
}
</script>
