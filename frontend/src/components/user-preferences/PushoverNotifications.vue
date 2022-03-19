<template>
  <section class="pushover">
    <h2 class="section-title">Pushover</h2>
    <small class="form-text text-muted">
      If you have a Pushover account, you can
      <a href="https://support.pushover.net/i7-what-is-pushover-and-how-do-i-use-it">get your User Key</a>
      and enter it here.
    </small>
    <br />
    <div class="form-group row">
      <label for="id_pushover_user_token" class="col-md-2 col-sm-3 col-form-label">User Key</label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <saving-animation :errors="errorMessages.pushover_user_token" :saving="saving.pushover_user_token">
          <input
            type="text"
            maxlength="256"
            placeholder="Pushover User Key"
            class="form-control"
            id="id_pushover_user_token"
            v-model="user.pushover_user_token"
          >
        </saving-animation>
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.print_notification_by_pushover" :saving="saving.print_notification_by_pushover">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_print_notification_by_pushover"
              v-model="user.print_notification_by_pushover"
              @change="$emit('updateSetting', 'print_notification_by_pushover')"
            >
            <label class="custom-control-label" for="id_print_notification_by_pushover">
              Send print job notifications via Pushover
            </label>
          </div>
        </saving-animation>
        <small class="text-muted">You will always be alerted via Pushover on print failures.</small>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'

export default {
  name: 'PushoverNotifications',

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
