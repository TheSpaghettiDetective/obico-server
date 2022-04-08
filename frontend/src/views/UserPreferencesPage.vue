<template>
  <layout>
    <template v-slot:content>
      <b-container fluid="xl" :class="{'is-in-mobile': useMobileLayout}" class="flex-full-size">
        <b-row class="flex-full-size">
          <b-col class="flex-full-size">
            <div v-if="user" class="flex-full-size">
              <!-- Mobile (web / app) -->
              <div v-if="useMobileLayout" class="mobile-settings-wrapper full-on-mobile">
                <div v-if="$route.path === '/user_preferences/'" class="mobile-settings-categories">
                  <h2 v-show="!onlyNotifications()" class="categories-title section-title">Account</h2>
                  <template v-for="(value, name) in sections">
                    <router-link v-if="!value.isHidden" :key="name" :to="value.route" :class="value.isSubcategory ? 'subcategory' : ''">
                      <span>
                        <i v-if="value.faIcon" :class="[value.faIcon, 'mr-2']" style="font-size: 1.125rem"></i>
                        <span>{{ value.title }}</span>
                      </span>
                      <i class="fas fa-arrow-right"></i>
                    </router-link>
                  </template>

                  <a v-if="!onlyNotifications()" href="#" @click.prevent="logout">
                    <span>
                      <i :class="['fas fa-sign-out-alt', 'mr-2']" style="font-size: 1.125rem"></i>
                      Logout
                    </span>
                  </a>
                </div>
                <div v-else class="mobile-settings-content" :class="{'is-in-mobile': useMobileLayout}">
                  <component
                    :is="currentRouteComponent"
                    :user="user"
                    :errorMessages="errorMessages"
                    :saving="saving"
                    :config="config"
                    @updateSetting="updateSetting"
                    @errorAlert="errorAlert"
                  ></component>
                </div>
              </div>
              <!-- Desktop -->
              <b-tabs
                v-else
                :vertical="true"
                class="desktop-settings-wrapper"
                nav-wrapper-class="settings-nav"
                active-nav-item-class=""
                content-class="desktop-settings-content"
                @activate-tab="updateRoute"
              >
                <template v-for="(value, name) in sections">
                  <b-tab
                    v-if="!value.isHidden"
                    :key="name"
                    :title-item-class="value.isSubcategory ? 'subcategory' : ''"
                    :active="$route.path === value.route"
                  >
                    <template #title>
                      <i v-if="value.faIcon" :class="[value.faIcon, 'mr-2']"></i>
                      {{ value.title }}
                    </template>
                    <component
                      :is="name"
                      :user="user"
                      :errorMessages="errorMessages"
                      :saving="saving"
                      :config="config"
                      @updateSetting="updateSetting"
                      @errorAlert="errorAlert"
                    ></component>
                  </b-tab>
                </template>
                <template #tabs-end>
                  <li class="nav-item">
                    <a class="nav-link" href="#" @click.prevent="logout">
                      <i :class="['fas fa-sign-out-alt', 'mr-2']"></i>
                      Logout
                    </a>
                  </li>
                </template>
              </b-tabs>
            </div>
            <div v-else class="text-center">
              <b-spinner class="mt-5" label="Loading..."></b-spinner>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'
import urls from '@config/server-urls'
import Layout from '@src/components/Layout.vue'
import { inMobileWebView, onlyNotifications } from '@src/lib/page_context'
import sections from '@config/user-preferences/sections'
import routes from '@config/user-preferences/routes'
import { mobilePlatform } from '@src/lib/page_context'

export default {
  name: 'UserPreferencesPage',

  props: {
    config: {
      default() {return {}},
      type: Object,
    },
  },

  components: {
    Layout,
    ...Object.keys(sections).reduce((obj, name) => {
      return Object.assign(obj, { [name]: sections[name].importComponent })
    }, {}),
  },

  data() {
    return {
      sections,
      onlyNotifications,
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
      useMobileLayout: false,
    }
  },

  computed: {
    visibleSections() {
      return Object.values(sections).filter(item => !item.isHidden)
    },
    currentRouteComponent() {
      for (const [component, route] of Object.entries(routes)) {
        if (this.$route.path === route) {
          return component
        }
      }
      return null
    },
    inMobileWebView() {
      return inMobileWebView()
    },
    clientIsThemeable() {
      return !inMobileWebView() || (new URLSearchParams(window.location.search).get('themeable') === 'true')
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
    // FIXME: come up with better solution to make android webview handle updateNavigationState
    currentRouteComponent() {
      if (mobilePlatform() === 'android') {
        this.$router.go()
      }
    },
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

  created() {
    this.fetchUser()
  },

  methods: {
    updateRoute(newTabIndex) {
      const section = Object.values(this.visibleSections)[newTabIndex]
      this.$router.replace({ path: section.route })
    },
    logout() {
      this.$swal.Confirm.fire({
        title: 'Confirmation',
        html: '<p class="text-center">You a going to logout from your account</p>',
        confirmButtonText: 'Logout',
        cancelButtonText: 'Cancel',
      }).then((result) => {
        if(result.isConfirmed) {
          window.location.replace('/accounts/logout/')
        }
      })
    },
    checkMobileLayout() {
      const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)
      this.useMobileLayout = inMobileWebView() || vw < 1140
    },
    fetchUser() {
      return axios
        .get(urls.user())
        .then(response => {
          this.user = response.data
        })
    },
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
          if (window.ReactNativeWebView) {
            if (key === 'first_name') {
              window.ReactNativeWebView.postMessage(JSON.stringify({firstName: this.firstName}))
            } else if (key === 'last_name') {
              window.ReactNativeWebView.postMessage(JSON.stringify({lastName: this.lastName}))
            }
          }

          this.setSavingStatus(key, false)
        })
    },
    checkForCombinedValues(propName) {
      for (const [key, inputs] of Object.entries(this.combinedInputs)) {
        if (inputs.includes(propName)) {
          return {inputs, key}
        }
      }
      return null
    },
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },
    errorAlert(text=null) {
      this.$swal({
        icon: 'error',
        html: `<p>${text ? text : 'Can not update your preferences.'}</p><p>Get help from <a href="https://discord.com/invite/NcZkQfj">TSD discussion forum</a> if this error persists.</p>`,
      })
    },
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
  mounted() {
    this.checkMobileLayout()
    window.onresize = this.checkMobileLayout
    if (this.useMobileLayout) {
      document.querySelector('body').style.paddingTop = '0px'
    }
  },
}
</script>

<style lang="sass" scoped>
$container-border-radius: 16px

.flex-full-size
  display: flex
  flex-direction: column
  flex: 1
.desktop-settings-wrapper
  margin: 0
  background-color: var(--color-surface-secondary)
  border-radius: $container-border-radius
  ::v-deep .desktop-settings-content
    padding: 2rem
    padding-right: 3rem
.mobile-settings-wrapper
  flex: 1
  background-color: var(--color-surface-secondary)
  padding: 1.5rem
  .mobile-settings-content
    padding-right: 1rem
  .mobile-settings-categories
    .categories-title
      font-weight: bold
      font-size: 1.5rem
      margin-bottom: 1rem
    a
      color: var(--text-primary)
      display: flex
      justify-content: space-between
      align-items: center
      padding: .8rem 0
      border-bottom: 1px solid var(--color-divider)
      font-size: 1.2em
      &.subcategory
        font-size: 1em
        padding-left: 1.625em
      i
        font-size: .8rem
::v-deep section:not(:first-child) .section-title
  margin-top: 2rem
::v-deep .section-title
  font-weight: bold
  font-size: 1.5rem
  padding-bottom: .25rem
  border-bottom: 1px solid var(--color-text-primary)
  margin-bottom: 1.5rem
::v-deep .settings-nav
  width: 25%
  background-color: var(--color-surface-primary)
  min-height: 80vh
  padding: 1.5rem 1rem
  border-radius: $container-border-radius 0 0 $container-border-radius
  .subcategory
    a
      padding-left: 3.125em
      font-size: 0.9em
  .active
    border-radius: 6px
  a
    border: initial
::v-deep .nav-tabs
  border-bottom: none
</style>