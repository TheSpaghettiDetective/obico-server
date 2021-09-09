<template>
  <div class="row justify-content-center">
    <pull-to-reveal>
      <navbar view-name="app.views.web_views.user_preferences"></navbar>
    </pull-to-reveal>

    <b-container class="wrapper" :class="{'is-in-mobile': isInMobile}">
      <b-row>
        <b-col>
          <div v-if="user">
            <!-- 2-step nav for mobiles -->
            <div class="mobile-settings-wrapper">
              <div v-if="$route.path === '/'" class="mobile-settings-categories">
                <h2 class="categories-title section-title">Preferences</h2>
                <router-link v-if="!isInMobile" to="/theme">
                  <span>Personalization</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/profile">
                  <span>Profile</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/email">
                  <span>Email</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>

                <h3 class="preferences-category-title">Notifications</h3>
                <router-link to="/general_notifications">
                  <span>General</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link v-if="isInMobile" to="/mobile_push_notifications" href="mobile_push_notifications">
                  <span>Push</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/email_notifications">
                  <span>Email</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/sms_notifications">
                  <span>SMS</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/pushbullet_notifications">
                  <span>Pushbullet</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/discord_notifications">
                  <span>Discord</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link to="/telegram_notifications">
                  <span>Telegram</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link v-if="pushOverEnabled" to="/pushover_notifications">
                  <span>Pushover</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
                <router-link v-if="slackEnabled" to="/slack_notifications">
                  <span>Slack</span>
                  <i class="fas fa-arrow-right"></i>
                </router-link>
              </div>
              <div v-else class="mobile-settings-content" :class="{'is-in-mobile': isInMobile}">
                <!-- General -->
                <theme-preferences v-if="$route.path === '/theme'"></theme-preferences>
                <profile-preferences v-if="$route.path === '/profile'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></profile-preferences>
                <email-preferences v-if="$route.path === '/email'" :user="user"></email-preferences>
                <!-- Notifications -->
                <general-notifications v-if="$route.path === '/general_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></general-notifications>
                <email-notifications v-if="$route.path === '/email_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></email-notifications>
                <sms-notifications v-if="$route.path === '/sms_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" :twilioEnabled="twilioEnabled" @updateSetting="updateSetting"></sms-notifications>
                <pushbullet-notifications v-if="$route.path === '/pushbullet_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></pushbullet-notifications>
                <discord-notifications v-if="$route.path === '/discord_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></discord-notifications>
                <telegram-notifications v-if="$route.path === '/telegram_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" :config="config" @updateSetting="updateSetting" :errorAlert="errorAlert"></telegram-notifications>
                <pushover-notifications v-if="$route.path === '/pushover_notifications'" :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></pushover-notifications>
                <slack-notifications v-if="$route.path === '/slack_notifications'"></slack-notifications>
              </div>
            </div>
            <!-- left-side nav for desktops -->
            <b-tabs
              :vertical="true"
              class="desktop-settings-wrapper"
              nav-wrapper-class="settings-nav"
              active-nav-item-class=""
              content-class="desktop-settings-content"
            >
              <b-tab title="Personalization">
                <theme-preferences></theme-preferences>
              </b-tab>
              <b-tab title="Profile">
                <profile-preferences :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></profile-preferences>
              </b-tab>
              <b-tab title="Email">
                <email-preferences :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></email-preferences>
              </b-tab>
              <b-tab title="Notifications" disabled title-item-class="mt-2"></b-tab>
              <b-tab title="General">
                <general-notifications :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></general-notifications>
              </b-tab>
              <b-tab title="Email">
                <email-notifications :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></email-notifications>
              </b-tab>
              <b-tab title="SMS">
                <sms-notifications :user="user" :errorMessages="errorMessages" :saving="saving" :twilioEnabled="twilioEnabled" @updateSetting="updateSetting"></sms-notifications>
              </b-tab>
              <b-tab title="Pushbullet">
                <pushbullet-notifications :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></pushbullet-notifications>
              </b-tab>
              <b-tab title="Discord">
                <discord-notifications :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></discord-notifications>
              </b-tab>
              <b-tab title="Telegram">
                <telegram-notifications :user="user" :errorMessages="errorMessages" :saving="saving" :config="config" @updateSetting="updateSetting" :errorAlert="errorAlert"></telegram-notifications>
              </b-tab>
              <b-tab v-if="pushOverEnabled" title="Pushover">
                <pushover-notifications :user="user" :errorMessages="errorMessages" :saving="saving" @updateSetting="updateSetting"></pushover-notifications>
              </b-tab>
              <b-tab v-if="slackEnabled" title="Slack">
                <slack-notifications></slack-notifications>
              </b-tab>
            </b-tabs>
          </div>
          <div v-else class="text-center">
            <b-spinner class="mt-5" label="Loading..."></b-spinner>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@lib/server_urls'
import PullToReveal from '@common/PullToReveal.vue'
import Navbar from '@common/Navbar.vue'
import { isMobile } from '@lib/app_platform'
import { Themes, theme, selectTheme, getTheme } from '../main/themes.js'
import ThemePreferences from './preferences_components/ThemePreferences'
import ProfilePreferences from './preferences_components/ProfilePreferences'
import EmailPreferences from './preferences_components/EmailPreferences'
import EmailNotifications from './preferences_components/EmailNotifications'
import SmsNotifications from './preferences_components/SmsNotifications'
import PushbulletNotifications from './preferences_components/PushbulletNotifications'
import DiscordNotifications from './preferences_components/DiscordNotifications'
import TelegramNotifications from './preferences_components/TelegramNotifications'
import PushoverNotifications from './preferences_components/PushoverNotifications'
import SlackNotifications from './preferences_components/SlackNotifications'
import GeneralNotifications from './preferences_components/GeneralNotifications'

export default {
  name: 'UserPreferencesRoute',

  components: {
    PullToReveal,
    Navbar,
    ThemePreferences,
    ProfilePreferences,
    EmailPreferences,
    EmailNotifications,
    SmsNotifications,
    PushbulletNotifications,
    DiscordNotifications,
    TelegramNotifications,
    PushoverNotifications,
    SlackNotifications,
    GeneralNotifications,
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
      combinedInputs: { // Send changes to API only if all the other values in the array have data
        phone: ['phone_country_code', 'phone_number'],
      },
      Themes: Themes,
      twilioEnabled: false,
      slackEnabled: false,
      pushOverEnabled: false,
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
      console.log('updateSetting, ', settingsItem)
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
  },

  mounted () {
    if (this.isInMobile) {
      document.querySelector('body').style.paddingTop = '0px'
      document.querySelector('body').style.background = 'rgb(var(--color-surface-secondary))'
    }
  },
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.wrapper
  &:not(.is-in-mobile)
    margin: 2.5rem 0

    @media (max-width: 768px)
      margin: 0

  .desktop-settings-wrapper
    background-color: rgb(var(--color-surface-secondary))

    @media (max-width: 768px)
      display: none

    ::v-deep .desktop-settings-content
      padding: 2rem
      padding-right: 3rem

  .mobile-settings-wrapper
    padding: 2rem 0

    @media (min-width: 769px)
      display: none

    .mobile-settings-content
      background-color: rgb(var(--color-surface-secondary))
      padding: 1.5rem 2.5rem 1.5rem 1.5rem

      &.is-in-mobile
        padding: 0 1.5rem

    .mobile-settings-categories
      .categories-title
        font-weight: bold
        font-size: 1.5rem
        margin-bottom: 1rem

      a
        color: rgb(var(--text-primary))
        display: flex
        justify-content: space-between
        align-items: center
        padding: .8rem 0
        border-bottom: 1px solid rgb(var(--color-divider))

        i
          font-size: .8rem

      .preferences-category-title
        margin: 0
        font-size: 1rem
        line-height: 1.5
        padding: 1.5rem 0 .8rem
        border-bottom: 1px solid rgb(var(--color-divider))
        color: rgb(var(--color-text-secondary))

::v-deep section:not(:first-child) .section-title
  margin-top: 2rem

::v-deep .section-title
  font-weight: bold
  font-size: 1.5rem
  margin-bottom: 1rem
  border-bottom: 1px solid rgb(var(--color-text-primary))

::v-deep .settings-nav
  width: 25%
  background-color: rgb(var(--color-surface-primary))
  min-height: 80vh
  padding: 1rem 0

  a
    border: initial

::v-deep .nav-tabs
  border-bottom: none
</style>
