<template>
  <b-container>
    <b-row class="justify-content-center">
      <b-col v-if="user" lg="8" class="mt-3">
        <div v-if="printersToShow.length === 0" class="wizard-container full-on-mobile">
          <b-container>
            <b-row>
              <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
                <svg viewBox="0 0 1965 240" class="logo-img">
                  <use href="#svg-logo-compact" />
                </svg>
              </div>
            </b-row>
            <b-row>
              <h1 class="mx-auto">{{$t("Welcome To")}} {{ $syndicateText.brandName }}</h1>
            </b-row>
            <b-row>
              <b-col>
                <hr />
              </b-col>
            </b-row>
            <b-row v-if="isEnt && trialDaysLeft > 0">
              <b-col>
                <h3 v-if="trialDaysLeft >= 29" class="py-3">
                  <i18next :translation="$t('Your 30-Day {localizedDom} Free Trial Has Started!')">
                    <template #localizedDom>
                      <a class="link" target="_blank" :href="getDocUrl('/user-guides/upgrade-to-pro/')">{{$t("Pro Plan")}}</a>
                    </template>
                  </i18next>
                </h3>
                <h3 v-else class="py-3">
                  <i18next :translation="$t('{trialDaysLeft} Days Left on Your {localizedDom} Free Trial!')">
                    <template #localizedDom>
                      <a class="link" target="_blank" :href="getDocUrl('/user-guides/upgrade-to-pro/')">{{$t("Pro Plan")}} </a>
                    </template>
                    <template #trialDaysLeft>
                      {{trialDaysLeft}}
                    </template>
                  </i18next>

                </h3>
                <div class="pb-1">
                  <i class="feature-check fas fa-check-circle"></i
                  ><span class="feature-text"
                    >{{ $t('Unlimited Secure Tunnel to your {platformDisplayName}',{platformDisplayName}) }}</span
                  >
                </div>
                <div class="pb-1">
                  <i class="feature-check fas fa-check-circle"></i
                  ><span class="feature-text">{{$t("Premium 25 FPS Webcam Streaming")}}</span>
                </div>
                <div class="pb-1">
                  <i class="feature-check fas fa-check-circle"></i
                  ><span class="feature-text">{{ $t("250 AI Failure Detection Hours") }}</span>
                </div>
                <div class="pb-1">
                  <i class="feature-check fas fa-check-circle"></i
                  ><span class="feature-text">{{ $t("G-Code Remote Upload and Printing") }}</span>
                </div>
                <div class="lead py-4">{{ $t("{platformDisplayName} has not been linked to your {brandName} account.",{platformDisplayName,brandName:$syndicateText.brandName}) }}</div>
                <div class="d-flex flex-column align-center justify-content-center">
                  <div>
                    <a :href="wizardUrl" class="btn btn-primary btn-block mx-auto btn-lg"
                      >{{ $t("Link {platformDisplayName} Now",{platformDisplayName}) }}</a
                    >
                  </div>
                  <div>
                    <div class="text-muted mx-auto text-center font-weight-light">
                      {{$t("It's as easy as 1-2-3.")}}
                    </div>
                  </div>
                </div>
              </b-col>
            </b-row>
            <div class="footer-note small">
              <i18next :translation="$t('Not ready to start yet? {localizedDom} to pause your free trial.')">
                <template #localizedDom>
                  <a href="mailto:support@obico.io?subject=Please%20pause%20my%20free%20trial">{{$t("Email us")}}</a>
                </template>
              </i18next>
            </div>
          </b-container>
        </div>
        <div v-else>
          <div class="text-center">
            <svg width="100" height="30">
              <use href="#svg-logo-full" />
            </svg>
          </div>

          <div v-if="authorized" class="authorization-successful">
            <h4 class="title">{{ $t("Authorization Successful!") }}</h4>
            <p>{{ $t("You can close this page") }}</p>
          </div>
          <div v-else>
            <div>
              <div class="lead text-center mt-3 mb-5">{{ $t("Tunnel Access Authorization") }}</div>
              <h4 class="my-4">
                <span class="font-weight-bold">{{appDisplayName}}</span>

                {{ $t('is requesting to access you {platformDisplayName} Tunnel.',{platformDisplayName}) }}
              </h4>
              <p class="text-muted">
                <a :href="getDocUrl('/user-guides/octoprint-tunneling/')" target="_blank">{{platformDisplayName}} {{$t("Tunnel")}}</a>
                <i18next :translation="$t('is a secure way provided by {localizedDom} to remotely access your {platformDisplayName}. With the {platformDisplayName} Tunnel, you can use {appDisplayName} to access your {platformDisplayName} from anywhere.')">
                    <template #localizedDom>
                      <a href="https://www.obico.io/" target="_blank">{{$syndicateText.brandName}}</a>
                    </template>
                    <template #platformDisplayName>
                      {{platformDisplayName}}
                    </template>
                    <template #appDisplayName>
                      {{appDisplayName}}
                    </template>
                  </i18next>
              </p>

              <b-alert v-if="!user.is_pro" variant="warning" dismissible class="my-3" show>
                <div>
                  <i class="fas fa-exclamation-triangle"></i>
                  <i18next :translation="$t('Tunnel usage of a free account is {localizedDom} to enjoy unlimited tunnel usage.')">
                    <template #localizedDom>
                      <a :href="getDocUrl('/user-guides/octoprint-tunneling/#why-is-the-limit-on-free-account-only-100mb')" target="_blank">{{$t("capped at 300MB per month")}}</a>. {{$t("You can")}} <a :href="getAppUrl('/ent_pub/pricing/')" target="_blank">{{$t("upgrade to the {brandName} app Pro plan for 1 Starbucks a month",{brandName:$syndicateText.brandName})}}</a>
                    </template>
                  </i18next>
                </div>
              </b-alert>
              <b-alert
                v-if="user.is_pro && trialDaysLeft > 0"
                variant="warning"
                dismissible
                class="my-3"
                show
              >
                <div>
                  <i class="fas fa-exclamation-triangle"></i>
                  <i18next :translation="$t('After the Free trial expires, tunnel data usage will be {localizedDom} to continue enjoying unlimited tunnel usage.')">
                    <template #localizedDom>
                      <a :href="getDocUrl('/user-guides/octoprint-tunneling/#why-is-the-limit-on-free-account-only-100mb')" target="_blank">{{$t("capped at 300MB per month")}}</a>. {{$t("You can")}} <a :href="getAppUrl('/ent_pub/pricing/')" target="_blank">{{$t("upgrade to the {brandName} app Pro plan for 1 Starbucks a month",{brandName:$syndicateText.brandName})}}</a>
                    </template>
                  </i18next>

                </div>
              </b-alert>

              <div class="mt-5">
                <p class="lead">
                  <i18next :translation="$t('Tunnel access by {localizedDom} (make sure you trust it)')">
                    <template #localizedDom>
                      <span class="font-weight-bold">{{appDisplayName}}</span>
                    </template>
                  </i18next>
                </p>
                <h5 v-if="printersToShow.length === 0">{{ $t("You have 0 active printers") }}</h5>
                <h5 v-else-if="printersToShow.length === 1" class="font-weight-bold">
                  {{ printersToShow[0].name }}
                </h5>
                <select
                  v-else-if="printersToShow.length > 1"
                  v-model="printerToAuthorize"
                  class="custom-select"
                >
                  <option :value="null" selected disabled>{{ $t("Please select a printer") }}</option>
                  <option v-for="printer in printersToShow" :key="printer.id" :value="printer.id">
                    {{ printer.name }}
                  </option>
                </select>
                <div v-if="printersToShow.length" class="d-flex mt-4 mb-3">
                  <button
                    class="btn btn-primary"
                    style="flex: 1"
                    :disabled="!printerToAuthorize || performingAuthRequest"
                    @click="authorize"
                  >
                    <b-spinner v-if="performingAuthRequest" small label="Loading..."></b-spinner>
                    <span v-else>{{ $t("Authorize") }}</span>
                  </button>
                  <a
                    class="btn btn-outline-secondary ml-2"
                    style="flex: 1"
                    href="/user_preferences/authorized_apps"
                    >{{ $t("Manage Apps") }}</a
                  >
                </div>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-muted small mb-1">{{ $t("Security notes") }}:</p>
              <ul class="text-muted small pl-4">
                <li>
                  {{ $t("The app can only access the tunnel, not your {brandName} account info such as your email address.",{brandName:$syndicateText.brandName}) }}
                </li>
                <li>
                  {{ $t("The access remains valid until explicitly revoked. You can revoke the access by going to Preferences -> Authorized Apps.") }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="text-center pt-3 w-100">
          <a class="btn btn-secondary" :href="logoutUrl">{{ $t("Log Out") }}</a>
        </div>
      </b-col>
      <b-col v-else class="mt-5">
        <div>
          <b-container>
            <div class="d-flex justify-content-center align-items-center">
              <img class="logo-icon" :src="appLogo" />
              <h3>&#8644;</h3>
              <svg class="logo-icon obico">
                <use href="#svg-logo-compact" />
              </svg>
              <h3>&#8644;</h3>
              <img class="logo-icon" :src="platformLogo" />
            </div>
            <div class="my-4">
              <div class="mx-auto text-center">
                <h4>{{ $t("Free {platformDisplayName} Tunnel",{platformDisplayName}) }}</h4>
                <div class="lead">{{ $t("Powered by {brandName}",{brandName:$syndicateText.brandName}) }}</div>
              </div>
            </div>
            <div class="account-details">
              <p>
                {{ $t("With the Free {platformDisplayName} Tunnel by {brandName}, you can now use {appDisplayName} to",{platformDisplayName,brandName:$syndicateText.brandName,appDisplayName}) }}
                  <a :href="getDocUrl('/user-guides/octoprint-tunneling/#why-is-the-limit-on-free-account-only-100mb')" target="_blank"> {{$t("securely control and monitor your printer from anywhere")}}</a>
              </p>
              <ul class="text-muted">
                <li>{{ $t("Unlimited realtime webcam at 0.1FPS.") }}</li>
                <li>{{ $t("300MB monthly tunnel data cap (excluding webcam streaming).") }}</li>
                <li>{{ $t("10 hours/mo AI failure detection.") }}</li>
              </ul>
              <div>
                🔥🔥🔥
                <i18next :translation="$t('Upgrade to {brandName} Pro Account ({localizedDom}) to get premium features')">
                    <template #localizedDom>
                      <a :href="getAppUrl('/ent_pub/pricing/')" target="_blank">{{$t("from $4/mo")}}</a>
                    </template>
                    <template #brandName>
                      {{$syndicateText.brandName}}
                    </template>
                  </i18next>
              </div>
              <ul>
                <li>📷{{ $t("Unlimited realtime webcam streaming.") }}</li>
                <li>📶 {{ $t("Unlimited tunnel data usage.") }}</li>
                <li>🤖 {{ $t("50 hours/mo AI failure detection.") }}</li>
                <li>
                  <a :href="getAppUrl('/ent_pub/pricing/')" target="_blank"
                    >{{ $t("And much more...") }}</a
                  >
                </li>
              </ul>
            </div>
            <div>
              <div class="my-5 w-100">
                <a class="btn btn-primary btn-block" :href="loginUrl">{{ $t("SIGN IN ") }}</a>
                <div class="text-center pt-3 w-100">
                  <div class="font-weight-light text-muted">{{ $t("- OR -") }}</div>
                  <a class="btn" :href="signupUrl">{{ $t("SIGN UP") }}</a>
                </div>
              </div>
            </div>
          </b-container>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@config/server-urls'
import { normalizedPrinter } from '@src/lib/normalizers'
import { user, settings } from '@src/lib/page-context'
import octopodLogo from '@static/img/octopod.webp'
import octoappLogo from '@static/img/octoapp.webp'
import polymerLogo from '@static/img/polymer.webp'
import printoidLogo from '@static/img/printoid.webp'
import mobilerakerLogo from '@static/img/mobileraker.webp'
import genericAppLogo from '@static/img/generic-app.png'
import octoprintLogo from '@static/img/octoprint_logo.png'
import klipperLogo from '@static/img/klipper_logo.jpg'

export default {
  name: 'NewOctoPrintTunnelPage',

  components: {},

  data() {
    return {
      user: null,
      printers: [],
      printerId: null,
      printerToAuthorize: null,
      performingAuthRequest: false,
      authorized: false,
    }
  },

  computed: {
    printersToShow() {
      return this.printerId
        ? this.printers.filter((printer) => printer.id == this.printerId)
        : this.printers
    },
    loginUrl() {
      return `/accounts/login/?hide_navbar=true&next=${encodeURIComponent(
        window.location.pathname + window.location.search
      )}`
    },
    logoutUrl() {
      return `/accounts/logout/?hide_navbar=true&next=${encodeURIComponent(
        window.location.pathname + window.location.search
      )}`
    },
    signupUrl() {
      return `/accounts/signup/?hide_navbar=true&next=${encodeURIComponent(
        window.location.pathname + window.location.search
      )}`
    },
    wizardUrl() {
      return `/printers/wizard/?redirectToTunnelCreation=${encodeURIComponent(
        window.location.pathname + window.location.search
      )}`
    },
    appName() {
      return new URLSearchParams(window.location.search).get('app') || 'Unknown App'
    },
    platform() {
      return new URLSearchParams(window.location.search).get('platform')
    },
    trialDaysLeft() {
      if (this.user?.subscription?.plan_id !== 'pro-trial') {
        return -1
      }
      return moment(this.user.subscription.expired_at).diff(moment(), 'days') + 1
    },
    appLogo() {
      switch (this.appName.toLowerCase()) {
        case 'octopod':
          return octopodLogo
        case 'printoid':
          return printoidLogo
        case 'polymer':
          return polymerLogo
        case 'octoapp':
          return octoappLogo
        case 'mobileraker-ios':
          return mobilerakerLogo
        case 'mobileraker-android':
          return mobilerakerLogo
        default:
          return genericAppLogo
      }
    },
    appDisplayName() {
      if (this.appName.toLowerCase().includes('mobileraker')) {
        return 'Mobileraker'
      }
      return this.appName
    },
    isKlipper() {
      if (this.platform) {
        if (this.platform.toLowerCase() === 'klipper') {
          return true
        }
      } else {
        if (this.appName.toLowerCase().includes('mobileraker')) {
          return true
        }
      }
      return false
    },
    platformLogo() {
      return this.isKlipper ? klipperLogo : octoprintLogo
    },
    platformDisplayName() {
      return this.isKlipper ? 'Klipper' : 'OctoPrint'
    },
  },

  created() {
    this.user = user()
    const { IS_ENT } = settings()
    this.isEnt = !!IS_ENT
    this.printerId = new URLSearchParams(window.location.search).get('printer_id')
    if (this.user) {
      this.fetchPrinters()
    }
  },

  methods: {
    fetchPrinters() {
      return axios.get(urls.printers()).then((response) => {
        response.data.forEach((p) => {
          this.printers.push(normalizedPrinter(p))
        })
        if (this.printersToShow.length == 1) {
          this.printerToAuthorize = this.printersToShow[0].id
        }
      })
    },

    authorize() {
      if (this.printersToShow.length) {
        this.performingAuthRequest = true
        axios
          .post(urls.tunnels(), {
            app_name: this.appName,
            target_printer_id: this.printerToAuthorize || this.printersToShow[0].id,
          })
          .then((response) => {
            this.authorized = true
            const tunnelEndpoint = response.data.tunnel_endpoint
            const redirectUrl =
              new URLSearchParams(window.location.search).get('success_redirect_url') ||
              '/tunnels/succeeded/'
            window.location.replace(`${redirectUrl}?tunnel_endpoint=${tunnelEndpoint}`)
          })
          .catch((error) => {
            this.performingAuthRequest = false
            this.errorDialog(error)
          })
      }
    },
  },
}
</script>

<style lang="sass" scoped>
body
  padding-bottom: 0

.wizard-container
  padding: 1.5rem 0.6rem 3rem

.feature-check
  color: var(--color-primary)

.feature-text
  margin-left: 0.5em

.authorization-successful
  padding-top: 6rem
  text-align: center

.logo-img
  max-height: 4em
  margin-bottom: 2em

.logo-icon
  max-height: 50px
  max-width: 50px
  margin: 0px 15px
  border-radius: 50%
  object-fit: cover

  &.obico
    max-width: 46px
    color: var(--color-primary)

.account-details
  background: var(--color-surface-secondary)
  border-radius: var(--border-radius-sm)
  padding: 15px
  margin-left: -15px
  margin-right: -15px

.footer-note
  margin: 3rem 0 -1.5rem
  text-align: right
</style>
