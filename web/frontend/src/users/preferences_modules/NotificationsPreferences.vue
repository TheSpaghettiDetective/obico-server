<template>
  <div>
    <!-- Notifications -->
    <section class="notifications">
      <h2 class="section-title">Notifications</h2>
      <div class="row">
        <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
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
        <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
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
        <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
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

    <!-- SMS -->
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
            <small class="text-muted">
              <div>Can't find your country code?</div>
              <div>The Spaghetti Detective Team is currently self-funded. Therefore we can't afford to open to
                countries with high SMS cost. We will add more countries once we find a cost-effective SMS solution,
                or secure sufficient funding.</div>
            </small>
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

    <!-- Pushbullet -->
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

    <!-- Discord -->
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

    <!-- Telegram -->
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

    <!-- pushover -->
    <section v-if="pushOverEnabled" class="pushover">
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

    <!-- Slack -->
    <section v-if="slackEnabled" class="slack">
      <h2 class="section-title">Slack</h2>
      <a href="/ent/slack_setup/">Set up Slack integration >>></a>
    </section>
  </div>
</template>

<script>
import axios from 'axios'
import {vueTelegramLogin} from 'vue-telegram-login'
import SavingAnimation from '@common/SavingAnimation.vue'


export default {
  name: 'NotificationsPreferences',

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

  created() {
    if (document.querySelector('#settings-json')) {
      const {TWILIO_ENABLED, SLACK_CLIENT_ID, PUSHOVER_APP_TOKEN} = JSON.parse(document.querySelector('#settings-json').text)
      this.twilioEnabled = !!TWILIO_ENABLED
      this.slackEnabled = !!SLACK_CLIENT_ID
      this.pushOverEnabled = !!PUSHOVER_APP_TOKEN
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