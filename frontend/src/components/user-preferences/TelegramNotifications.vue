<template>
  <section v-if="config.telegramBotName" class="telegram">
    <h2 class="section-title">Telegram</h2>
    <small class="form-text text-muted">
      Login to be notified by our Telegram bot.
    </small>
    <br>
    <div class="form-group row">
      <div v-if="user.telegram_chat_id">
        <div class="col-md-50">
          <div class="btn btn-sm btn-primary float-left mr-2" id="id_telegram_logout_btn" @click="onTelegramLogout">Unlink Telegram</div>
          <div class="btn btn-sm btn-primary float-left" id="id_telegram_test_btn" @click="onTelegramTest($event)">Test Telegram Notification</div>
        </div>
      </div>
      <div v-else>
        <vue-telegram-login
          mode="callback"
          :telegram-login="config.telegramBotName"
          request-access="write"
          @callback="onTelegramAuth" />
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.print_notification_by_telegram" :saving="saving.print_notification_by_telegram">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_print_notification_by_telegram"
              v-model="user.print_notification_by_telegram"
              @change="$emit('updateSetting', 'print_notification_by_telegram')"
            >
            <label class="custom-control-label" for="id_print_notification_by_telegram">
              Send print job notifications via Telegram
            </label>
          </div>
        </saving-animation>
        <small class="text-muted">You will always be alerted via Telegram on print failures.</small>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'
import {vueTelegramLogin} from 'vue-telegram-login'
import SavingAnimation from '@src/components/SavingAnimation.vue'

export default {
  name: 'TelegramNotifications',

  components: {
    SavingAnimation,
    vueTelegramLogin,
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
    config: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      twilioEnabled: false,
      slackEnabled: false,
      pushOverEnabled: false,
    }
  },

  methods: {
    onTelegramAuth(telegram_user) {
      this.user.telegram_chat_id = JSON.stringify(telegram_user.id)
      this.$emit('updateSetting', 'telegram_chat_id')
      // this.updateSetting('telegram_chat_id')
    },

    onTelegramLogout() {
      this.user.telegram_chat_id = null
      this.$emit('updateSetting', 'telegram_chat_id')
      // this.updateSetting('telegram_chat_id')
    },

    onTelegramTest(event) {
      event.target.classList.add('disabled')

      return axios
        .post('/test_telegram')
        .then(() => {
          event.target.classList.add('btn-success')
        })
        .catch(err => {
          this.$emit('errorAlert', 'Telegram test failed.')
          // this.errorAlert('Telegram test failed.')
          console.log(err)
        })
    }
  },
}
</script>
