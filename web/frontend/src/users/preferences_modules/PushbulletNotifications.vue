<template>
  <section class="pushbullet">
    <h2 class="section-title">Pushbullet</h2>
    <small class="form-text text-muted">
      If you have a Pushbullet account, you can
      <a href="https://www.pushbullet.com/#settings">generate an access token</a>
      and enter it here.
    </small>
    <br>
    <div class="form-group row">
      <label for="id_pushbullet_access_token" class="col-md-2 col-sm-3 col-form-label">Access Token</label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <saving-animation :errors="errorMessages.pushbullet_access_token" :saving="saving.pushbullet_access_token">
          <input
            type="text"
            maxlength="45"
            placeholder="Pushbullet Access Token"
            class="form-control"
            id="id_pushbullet_access_token"
            v-model="user.pushbullet_access_token"
          >
        </saving-animation>
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.print_notification_by_pushbullet" :saving="saving.print_notification_by_pushbullet">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_print_notification_by_pushbullet"
              v-model="user.print_notification_by_pushbullet"
              @change="$emit('updateSetting', 'print_notification_by_pushbullet')"
            >
            <label class="custom-control-label" for="id_print_notification_by_pushbullet">
              Send print job notifications via PushPullet
            </label>
          </div>
        </saving-animation>
        <small class="text-muted">You will always be alerted via PushPullet on print failures.</small>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@common/SavingAnimation.vue'

export default {
  name: 'PushbulletNotifications',

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