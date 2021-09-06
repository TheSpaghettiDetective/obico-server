<template>
  <div class="row justify-content-center">
    <pull-to-reveal>
      <navbar view-name="app.views.web_views.user_preferences"></navbar>
    </pull-to-reveal>

    <div class="col-sm-11 col-md-10 col-lg-8">
      <div v-if="user" class="form-container">
        <!-- Personalization -->
        <section v-if="!isInMobile" class="personalization">
          <h2 class="section-title">Personalization</h2>
          <div class="form-group row mt-3">
            <label class="col-md-2 col-sm-3 col-form-label">Theme</label>
            <div class="col-sm-9 col-md-10">
              <div class="theme-controls">
                <div class="theme-toggle" :class="[themeValue]" @click="toggleTheme">
                  <svg viewBox="0 0 39.68 39.68" fill="currentColor" class="icon" :class="{'active': themeValue === Themes.Dark}">
                    <use href="#svg-moon-icon" />
                  </svg>
                  <div class="label">
                    <span class="dark" v-show="themeValue === Themes.Dark">DARK</span>
                    <span class="light" v-show="themeValue === Themes.Light">LIGHT</span>
                  </div>
                  <svg viewBox="0 0 42.07 42.07" fill="currentColor" class="icon" :class="{'active': themeValue === Themes.Light}">
                    <use href="#svg-sun-icon" />
                  </svg>
                  <div class="active-indicator" :class="{'right': themeValue === Themes.Light}">
                    <div class="circle"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
                <div class="custom-control custom-checkbox form-check-inline system-theme-control">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_theme_system"
                    v-model="systemTheme"
                  >
                  <label class="custom-control-label" for="id_theme_system">
                    Sync theme with system settings
                  </label>
                </div>
            </div>
          </div>
        </section>

        <!-- Profile -->
        <section class="profile">
          <h2 class="section-title">Profile</h2>
          <div class="form-group row">
            <label class="col-md-2 col-sm-3 col-form-label">Password</label>
            <div class="col-md-10 col-sm-9 col-form-label text-muted">
              <a href="/accounts/password/change">Change</a>
            </div>
          </div>
          <div class="form-group row">
            <label for="id_first_name" class="col-md-2 col-sm-3 col-form-label">First Name</label>
            <div class="col-md-10 col-sm-9">
              <saving-animation :errors="errorMessages.first_name" :saving="saving.first_name">
                <input
                  type="text"
                  maxlength="30"
                  class="form-control"
                  id="id_first_name"
                  v-model="user.first_name"
                >
              </saving-animation>
            </div>
          </div>
          <div class="form-group row">
            <label for="id_last_name" class="col-md-2 col-sm-3 col-form-label">Last Name</label>
            <div class="col-md-10 col-sm-9">
              <saving-animation :errors="errorMessages.last_name" :saving="saving.last_name">
                <input
                  type="text"
                  maxlength="30"
                  class="form-control"
                  id="id_last_name"
                  v-model="user.last_name"
                >
              </saving-animation>
            </div>
          </div>
        </section>

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
                    @change="updateSetting('notify_on_done')"
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
                    @change="updateSetting('notify_on_canceled')"
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
                    @change="updateSetting('account_notification_by_email')"
                  >
                  <label class="custom-control-label" for="id_account_notification_by_email">
                    Notify me on account events (such as running out of Detective Hours)
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
        </section>

        <!-- Email -->
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
                    @change="updateSetting('alert_by_email')"
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
                    @change="updateSetting('print_notification_by_email')"
                  >
                  <label class="custom-control-label" for="id_print_notification_by_email">
                    Send print job notifications to all verified email addresses
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
                    @change="updateSetting('alert_by_sms')"
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
                    @change="updateSetting('print_notification_by_pushbullet')"
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
                    @change="updateSetting('print_notification_by_discord')"
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
                    @change="updateSetting('print_notification_by_telegram')"
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
          <h2>Pushover</h2>
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
                    @change="updateSetting('print_notification_by_pushover')"
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
      <div v-else class="text-center">
        <b-spinner class="mt-5" label="Loading..."></b-spinner>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@lib/server_urls'
import SavingAnimation from '../common/SavingAnimation.vue'
import PullToReveal from '@common/PullToReveal.vue'
import Navbar from '@common/Navbar.vue'
import {vueTelegramLogin} from 'vue-telegram-login'
import { Themes, theme, selectTheme, getTheme } from '../main/themes.js'
import { isMobile } from '@lib/app_platform'

export default {
  name: 'UserPreferencesRoute',
  components: {
    SavingAnimation,
    vueTelegramLogin,
    PullToReveal,
    Navbar,
  },

  data() {
    return {
      user: null,
      saving: {},
      errorMessages: {},
      delayedSubmit: { // Make pause before sending new value to API
        'first_name': {
          'delay': 1000,
          'timeoutId': null
        },
        'last_name': {
          'delay': 1000,
          'timeoutId': null
        },
        'pushbullet_access_token': {
          'delay': 1000,
          'timeoutId': null
        },
        'discord_webhook': {
          'delay': 1000,
          'timeoutId': null
        },
        'phone_number': {
          'delay': 1000,
          'timeoutId': null
        },
        'pushover_user_token': {
          'delay': 1000,
          'timeoutId': null
        },
        'telegram_chat_id': {
          'delay': 1000,
          'timeoutId': null
        }
      },
      twilioEnabled: false,
      slackEnabled: false,
      pushOverEnabled: false,
      combinedInputs: { // Send changes to API only if all the other values in the array have data
        phone: ['phone_country_code', 'phone_number'],
      },
      Themes: Themes,
    }
  },

  computed: {
    themeValue() {
      return getTheme()
    },
    systemTheme: {
      get() {
        return theme.value === Themes.System
      },
      set(newValue) {
        theme.value = Themes.System
        if (newValue) {
          selectTheme(this.Themes.System)
        }
      }
    },
    firstName: {
      get: function() {
        return this.user ? this.user.first_name : undefined
      },
      set: function(newValue) {
        this.user.first_name = newValue
      }
    },
    lastName: {
      get: function() {
        return this.user ? this.user.last_name : undefined
      },
      set: function(newValue) {
        this.user.last_name = newValue
      }
    },
    phoneCountryCode: {
      get: function() {
        return this.user ? this.user.phone_country_code : undefined
      },
      set: function(newValue) {
        this.user.phone_country_code = newValue
      }
    },
    phoneNumber: {
      get: function() {
        return this.user ? this.user.phone_number : undefined
      },
      set: function(newValue) {
        this.user.phone_number = newValue
      }
    },
    pushbulletToken: {
      get: function() {
        return this.user ? this.user.pushbullet_access_token : undefined
      },
      set: function(newValue) {
        this.user.pushbullet_access_token = newValue
      }
    },
    discordWebhook: {
      get: function() {
        return this.user ? this.user.discord_webhook : undefined
      },
      set: function(newValue) {
        this.user.discord_webhook = newValue
      }
    },
    pushoverUserToken: {
      get: function() {
        return this.user ? this.user.pushover_user_token : undefined
      },
      set: function(newValue) {
        this.user.pushover_user_token = newValue
      }
    },
    telegramChatId: {
      get: function() {
        return this.user ? this.user.telegram_chat_id : undefined
      },
      set: function(newValue) {
        this.user.telegram_chat_id = newValue
      }
    },
  },

  watch: {
    firstName: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('first_name')
      }
    },
    lastName: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('last_name')
      }
    },
    phoneCountryCode: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.errorMessages.phone = []

        // Allow clear data
        if (newValue === '') {
          this.updateSetting('phone_country_code')
          return
        }

        const codeNumber = parseInt(newValue.replace(/\s/g, '')) // will parse both '1' / '+1', clear spaces for safety
        if (isNaN(codeNumber)) {
          return
        }

        if (this.config.twilioCountryCodes && (this.config.twilioCountryCodes.length !== 0) && !this.config.twilioCountryCodes.includes(codeNumber)) {
          this.errorMessages.phone = ['Oops, we don\'t send SMS to this country code']
        } else {
          this.updateSetting('phone_country_code')
        }
      }
    },
    phoneNumber: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('phone_number')
      }
    },
    pushbulletToken: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('pushbullet_access_token')
      }
    },
    discordWebhook: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('discord_webhook')
      }
    },
    pushoverUserToken: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('pushover_user_token')
      }
    },
    telegramChatId: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('telegram_chat_id')
      }
    }
  },

  props: {
    config: {
      default() {return {}},
      type: Object,
    },
  },

  created() {
    if (document.querySelector('#settings-json')) {
      const {TWILIO_ENABLED, SLACK_CLIENT_ID, PUSHOVER_APP_TOKEN} = JSON.parse(document.querySelector('#settings-json').text)
      this.twilioEnabled = !!TWILIO_ENABLED
      this.slackEnabled = !!SLACK_CLIENT_ID
      this.pushOverEnabled = !!PUSHOVER_APP_TOKEN
    }
    this.isInMobile = isMobile() || window.location.pathname.startsWith('/mobile/') || new URLSearchParams(window.location.search).get('inMobile') === 'true'
    this.fetchUser()
  },

  methods: {
    /**
     * Toggle color theme
     */
    toggleTheme() {
      const newTheme = this.themeValue === Themes.Light ? Themes.Dark : Themes.Light
      this.systemTheme = false
      selectTheme(newTheme)
    },

    /**
     * Get actual user preferences
     */
    fetchUser() {
      return axios
        .get(urls.user())
        .then(response => {
          this.user = response.data
        })
    },

    /**
     * Update user settings
     * @param {String} propName
     * @param {any} propValue
     */
    patchUser(propName, propValue) {
      let data = {}

      let key = propName
      const combinedInputs = this.checkForCombinedValues(propName)
      if (combinedInputs) {
        // Must include all the inputs from the array
        // or don't send if some of them have no data
        for (const input of combinedInputs.inputs) {
          key = combinedInputs.key
          const value = this.user[input]
          data[input] = value
        }

        // Allow either completely empty or completely filled data
        const values = Object.values(data)
        const emptyValues = values.filter(val => !val)
        if ((emptyValues.length !== values.length) && (emptyValues.length !== 0)) {
          return
        }
      } else {
        data = {[propName]: propValue}
      }

      this.setSavingStatus(key, true)

      // Make request to API
      return axios
        .patch(urls.user(), data)
        .catch(err => {
          if (err.response && err.response.data && typeof err.response.data === 'object') {
            if (err.response.data.non_field_errors) {
              this.errorAlert(err.response.data.non_field_errors)
            } else {
              for (const error in err.response.data) {
                this.errorMessages[key] = err.response.data[error]
              }
            }
          } else {
            this.errorAlert()
          }
        })
        .then(() => {
          this.setSavingStatus(key, false)
        })
    },

    /**
     * Checks if value is associated with others (must be sent simultaneously)
     * and returns array of input names in the collection
     * @param {String} propName
     * @return {Array, Boolean} array with input names or False
     */
    checkForCombinedValues(propName) {
      for (const [key, inputs] of Object.entries(this.combinedInputs)) {
        if (inputs.includes(propName)) {
          return {inputs, key}
        }
      }

      return null
    },

    /**
     * Interlayer for saving status control to be able to set same saving status
     * for 2 or more different inputs grouped to one block
     * @param {String} propName
     * @param {String} status
     */
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert(text=null) {
      this.$swal({
        icon: 'error',
        html: `<p>${text ? text : 'Can not update your preferences.'}</p><p>Get help from <a href="https://discord.com/invite/NcZkQfj">TSD discussion forum</a> if this error persists.</p>`,
      })
    },

    /**
     * Update particular settings item
     * @param {String} settingsItem
     */
    updateSetting(settingsItem) {
      if (settingsItem in this.delayedSubmit) {
        const delayInfo = this.delayedSubmit[settingsItem]
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }
        this.delayedSubmit[settingsItem]['timeoutId'] = setTimeout(() => {
          this.patchUser(settingsItem, this.user[settingsItem])
        }, delayInfo['delay'])
        return
      }

      this.patchUser(settingsItem, this.user[settingsItem])
    },

    onTelegramAuth(telegram_user) {
      this.user.telegram_chat_id = JSON.stringify(telegram_user.id)
      this.updateSetting('telegram_chat_id')
    },

    onTelegramLogout() {
      this.user.telegram_chat_id = null
      this.updateSetting('telegram_chat_id')
    },

    onTelegramTest(event) {
      event.target.classList.add('disabled')

      return axios
        .post('/test_telegram')
        .then(() => {
          event.target.classList.add('btn-success')
        })
        .catch(err => {
          this.errorAlert('Telegram test failed.')
          console.log(err)
        })
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

section:not(:first-child)
  margin-top: 60px

.theme-controls
  display: flex
  align-items: center

.theme-toggle
  display: inline-flex
  align-items: center
  background-color: rgb(var(--color-input-background))
  border-radius: 100px
  position: relative
  margin-right: 26px

  &:hover
    cursor: pointer

  & > *
    position: relative
    z-index: 2

  .icon
    flex: 0 0 18px
    height: 18px
    margin: 10px
    color: #ABB6C2

    &.active
      color: #4B5B69

  .label
    flex: 1
    text-align: center
    font-size: 12px
    color: rgb(var(--color-text-primary))
    padding: 0 8px

  .active-indicator
    position: absolute
    width: calc(100% - 8px)
    height: 30px
    top: 0
    bottom: 0
    left: 0
    right: 0
    margin: auto
    z-index: 1
    transition: all .3s ease-out

    .circle
      position: absolute
      width: 30px
      height: 30px
      border-radius: 30px
      background-color: #fff
      transition: all .3s ease-in-out

    &.right
      transform: translateX(100%)

      .circle
        transform: translateX(-100%)

.system-theme-control
  position: relative
  z-index: 3

</style>
