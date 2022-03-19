<template>
  <section class="discord">
    <h2 class="section-title">Discord</h2>
    <small class="form-text text-muted">
      If you have a Discord channel you wish to receive notifications on, you can
      <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks">generate webhook url</a>
      and enter it here.
    </small>
    <br>
    <div class="form-group row">
      <label for="id_discord_webhook" class="col-md-2 col-sm-3 col-form-label">Webhook URL</label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <saving-animation :errors="errorMessages.discord_webhook" :saving="saving.discord_webhook">
          <input
            type="text"
            maxlength="256"
            placeholder="Discord Webhook"
            class="form-control"
            id="id_discord_webhook"
            v-model="user.discord_webhook"
          >
        </saving-animation>
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.print_notification_by_discord" :saving="saving.print_notification_by_discord">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_print_notification_by_discord"
              v-model="user.print_notification_by_discord"
              @change="$emit('updateSetting', 'print_notification_by_discord')"
            >
            <label class="custom-control-label" for="id_print_notification_by_discord">
              Send print job notifications via Discord Webhook
            </label>
          </div>
        </saving-animation>
        <small class="text-muted">You will always be alerted via Discord on print failures.</small>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@src/components/SavingAnimation.vue'

export default {
  name: 'DiscordNotifications',

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
