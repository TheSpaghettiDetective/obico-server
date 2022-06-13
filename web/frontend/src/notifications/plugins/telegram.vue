<template>
  <notification-channel-template
    :errorMessages="errorMessages"
    :saving="saving"
    :notificationChannel="notificationChannel"
    :showSettings="!!config.telegramBotName"

    @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
    @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <small class="form-text text-muted">
        Login to be notified by our Telegram bot.
      </small>
      <br>
      <div class="form-group row">
        <div v-if="notificationChannel.channelInfo && notificationChannel.channelInfo.config && notificationChannel.channelInfo.config.chat_id">
          <div class="col-12">
            <div class="btn btn-sm btn-primary float-left mr-2" @click="onTelegramLogout">Unlink Telegram</div>
            <div class="btn btn-sm btn-primary float-left" @click="onTelegramTest($event)">Test Telegram Notification</div>
          </div>
        </div>
        <div v-else>
          <div class="col-12">
          <vue-telegram-login
            mode="callback"
            :telegram-login="config.telegramBotName"
            request-access="write"
            @callback="onTelegramAuth" />
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
import {vueTelegramLogin} from 'vue-telegram-login'

export default {
  name: 'telegram',

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

  methods: {
    onTelegramAuth(telegram_user) {
      const config = { chat_id: JSON.stringify(telegram_user.id) }
      this.$emit('createNotificationChannel', this.notificationChannel, config)
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
        .catch(err => {
          event.target.classList.remove('disabled')
          this.$emit('errorAlert', 'Telegram test failed.')
          console.log(err)
        })
    }
  },
}
</script>
