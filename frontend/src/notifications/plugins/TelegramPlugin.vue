<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    :show-settings="setupCompleted"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <div class="form-text">
        <p>Login to be notified by our Telegram bot.</p>
        <div v-if="isInMobile" class="text-warning small">
          <p>
            Telegram in the mobile app is very finicky. Please open a browser, and log into
            <a href="https://app.obico.io">the {{ $t('brand_name') }} web app</a> using the same credential to set up
            Telegram.
          </p>
          <p>Once set up, Telegram notification will work properly on your phone.</p>
        </div>
        <div v-else class="text-warning small">
          <p>
            If you see "Bot domain invalid", please hard-refresh the browser a few times. I know
            it's annoying. But Telegram API has a very high failure rate.
          </p>
          <p>
            If you press the "Test Telegram Notification" button and see an error, please
            hard-refresh the browser a few times and press the test button again.
          </p>
        </div>
      </div>
      <br />
      <div class="form-group row">
        <div
          v-if="
            notificationChannel.channelInfo &&
            notificationChannel.channelInfo.config &&
            notificationChannel.channelInfo.config.chat_id
          "
        >
          <div class="col-12">
            <div class="btn btn-sm btn-primary float-left mr-2" @click="onTelegramLogout">
              Unlink Telegram
            </div>
            <div class="btn btn-sm btn-primary float-left" @click="onTelegramTest($event)">
              Test Telegram Notification
            </div>
          </div>
        </div>
        <div v-else>
          <div class="col-12">
            <vue-telegram-login
              mode="callback"
              :telegram-login="notificationChannel.pluginInfo.env_vars.TELEGRAM_BOT_NAME.value"
              request-access="write"
              @callback="onTelegramAuth"
            />
          </div>
        </div>
      </div>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'
import axios from 'axios'
import urls from '@config/server-urls'
import { vueTelegramLogin } from 'vue-telegram-login'
import { mobilePlatform } from '@src/lib/page-context'

export default {
  name: 'TelegramPlugin',

  components: {
    NotificationChannelTemplate,
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
    notificationChannel: {
      type: Object,
      required: true,
    },
    config: {
      type: Object,
      required: true,
    },
  },

  computed: {
    setupCompleted() {
      return !!this.notificationChannel.channelInfo?.config?.chat_id
    },
    isInMobile() {
      return mobilePlatform()
    },
  },

  methods: {
    onTelegramAuth(telegram_user) {
      const config = { chat_id: JSON.stringify(telegram_user.id) }
      this.$emit('createNotificationChannel', { section: this.notificationChannel, config })
    },

    onTelegramLogout() {
      this.$emit('deleteNotificationChannel', this.notificationChannel)
    },

    onTelegramTest(event) {
      event.target.classList.add('disabled')

      return axios
        .post(urls.testNotificationChannel(this.notificationChannel.channelInfo.id))
        .then(() => {
          event.target.classList.add('btn-success')
        })
        .catch((err) => {
          event.target.classList.remove('disabled')
          this.$swal.Reject.fire({
            title: 'Error',
            html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
              Telegram test failed
            </p>`,
            showConfirmButton: false,
            showCancelButton: true,
            cancelButtonText: 'Close',
          })
        })
    },
  },
}
</script>
