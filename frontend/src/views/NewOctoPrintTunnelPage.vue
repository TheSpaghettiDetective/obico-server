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
              <h1 class="mx-auto">Welcome To Obico</h1>
            </b-row>
            <b-row>
              <b-col>
                <hr />
              </b-col>
            </b-row>
            <b-row v-if="isEnt && trialDaysLeft > 0">
              <h3 v-if="trialDaysLeft >= 29" class="mx-auto pt-3 text-center">Your 30-Day <a class="link" target="_blank" href="https://www.obico.io/docs/user-guides/upgrade-to-pro/">Pro Plan</a> Free Trial Has Started!</h3>
              <h3 v-else class="mx-auto pt-3 text-center">{{trialDaysLeft}} Days Left on Your <a class="link" target="_blank" href="https://www.obico.io/docs/user-guides/upgrade-to-pro/">Pro Plan </a>Free Trial!</h3>
              <div class="mt-3 col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
                <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">Unlimited Secure Tunneling to your OctoPrint</span></div>
                <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">Premium 25fps Webcam Streaming</span></div>
                <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">250 AI Failure Detection Hours</span></div>
                <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">G-Code Remote Upload and Printing</span></div>
              </div>
            </b-row>
            <b-row>
              <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center">
                <p class="lead mt-5">OctoPrint has not been linked to your Obico account.</p>
                <div>
                  <a :href="wizardUrl" class="btn btn-primary btn-block mx-auto btn-lg">Link OctoPrint Now</a>
                </div>
                <div>
                  <div class="text-muted mx-auto text-center font-weight-light">It's as easy as 1-2-3.</div>
                </div>
              </div>
            </b-row>
          </b-container>
        </div>
        <div v-else>
          <div class="text-center">
            <svg width="100" height="30">
              <use href="#svg-logo-full" />
            </svg>
          </div>

          <div v-if="authorized" class="authorization-successful">
            <h4 class="title">Authorization Successful!</h4>
            <p>You can close this page</p>
          </div>
          <div v-else>
            <div>
              <h4 class="text-center my-5">OctoPrint Tunnel Access Authorization</h4>
              <p class="lead"><span class="font-weight-bold">{{ appName }}</span> is requesting to access the OctoPrint Tunnel.</p>
              <p class="text-muted"><a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/" target="_blank">OctoPrint Tunnel</a> is a secure way provided by the Obico app to securely access your OctoPrint. With the OctoPrint Tunnel, you can use {{appName}} to access your OctoPrint from anywhere.</p>

              <b-alert v-if="!user.is_pro" variant="warning" dismissible class="my-3" show>
                <div>
                  <i class="fas fa-exclamation-triangle"></i> Tunnel usage of a free account is <a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/#why-is-the-limit-on-free-account-only-50mb" target="_blank">capped at 50MB per month</a>. You can <a href="http://app.obico.io/ent_pub/pricing/" target="_blank">upgrade to the Obico app Pro plan for 1 Starbucks a month</a> to enjoy unlimited tunnel usage.
                </div>
              </b-alert>
              <b-alert v-if="user.is_pro && trialDaysLeft > 0" variant="warning" dismissible class="my-3" show>
                <div>
                  <i class="fas fa-exclamation-triangle"></i> After the Free trial expires, tunnel data usage will be <a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/#why-is-the-limit-on-free-account-only-50mb" target="_blank">capped at 50MB per month</a>. You can <a href="http://app.obico.io/ent_pub/pricing/" target="_blank">upgrade to the Obico app Pro plan for 1 Starbucks a month</a> to continue enjoying unlimited tunnel usage.
                </div>
              </b-alert>

              <div class="mt-5">
                <p class="lead">Tunnel access by <span class="font-weight-bold">{{ appName }}</span> (make sure you trust it):
                <h5 v-if="printersToShow.length === 0">You have 0 active printers</h5>
                <h5 v-else-if="printersToShow.length === 1" class="font-weight-bold">{{ printersToShow[0].name }}</h5>
                <select v-else-if="printersToShow.length > 1" v-model="printerToAuthorize" class="custom-select">
                  <option :value="null" selected disabled>Please select a printer</option>
                  <option
                    v-for="printer in printersToShow"
                    :key="printer.id"
                    :value="printer.id"
                  >
                    {{ printer.name }}
                  </option>
                </select>
                <div v-if="printersToShow.length" class="d-flex mt-4 mb-3">
                  <button
                    class="btn btn-primary"
                    style="flex: 1"
                    @click="authorize"
                    :disabled="!printerToAuthorize || performingAuthRequest"
                  >
                    <b-spinner v-if="performingAuthRequest" small label="Loading..."></b-spinner>
                    <span v-else>Authorize</span>
                  </button>
                  <a class="btn btn-outline-secondary ml-2" style="flex: 1" href="/user_preferences/authorized_apps">Manage Apps</a>
                </div>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-muted small mb-1">
                Security notes:
              </p>
              <ul class="text-muted small pl-4">
                <li>The app can only access the tunnel, not your Obico account info such as your email address.</li>
                <li>The access remains valid until explicitly revoked. You can revoke the access by going to Preferences -> Authorized Apps.</li>
              </ul>
            </div>
          </div>
        </div>
      </b-col>
      <b-col v-else class="mt-5">
        <div>
          <b-container>
            <b-row>
                <svg class="logo-img mx-auto">
                  <use href="#svg-logo-full" />
                </svg>
            </b-row>
            <b-row>
              <h5 class="mx-auto">FOR</h5>
            </b-row>
            <b-row>
              <h1 class="mx-auto">{{appName}}</h1>
            </b-row>
            <b-row class="justify-content-center">
              <p class="text-muted mt-5">The Obico app provides <a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/" target="_blank">free and secure remote access to your OctoPrint</a>.</p>
              <p class="text-muted">With the Obico app, you can now use {{appName}} to control and monitor your printer from anywhere.</p>
            </b-row>
            <b-row>
              <div class="my-5 w-100">
                <a class="btn btn-primary btn-block" :href="loginUrl">SIGN IN </a>
                <div class="text-center pt-3 w-100">
                  <div class="font-weight-light text-muted">- OR -</div>
                  <a class="btn" :href="signupUrl">SIGN UP</a>
                </div>
              </div>
            </b-row>
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
import { user, settings} from '@src/lib/page_context'

export default {
  name: 'NewOctoPrintTunnelPage',

  components: {
  },

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

  created() {
    this.user = user()
    const {IS_ENT} = settings()
    this.isEnt = !!IS_ENT
    this.printerId = new URLSearchParams(window.location.search).get('printer_id')
    if (this.user) {
      this.fetchPrinters()
    }
  },

  computed: {
    printersToShow() {
      return this.printerId ? this.printers.filter((printer) => printer.id == this.printerId) : this.printers
    },
    loginUrl() {
      return `/accounts/login/?hide_navbar=true&next=${encodeURIComponent(window.location.pathname+window.location.search)}`
    },
    signupUrl() {
      return `/accounts/signup/?hide_navbar=true&next=${encodeURIComponent(window.location.pathname+window.location.search)}`
    },
    wizardUrl() {
      return `/printers/wizard/?redirectToTunnelCreation=${encodeURIComponent(window.location.pathname+window.location.search)}`
    },
    appName() {
      return new URLSearchParams(window.location.search).get('app') || 'Unknown App'
    },
    trialDaysLeft() {
      if (this.user?.subscription?.plan_id !== 'pro-trial') {
        return -1
      }
      return moment(this.user.subscription.expired_at).diff(moment(), 'days') + 1
    }
  },

  methods: {
    fetchPrinters() {
      return axios
        .get(urls.printers())
        .then(response => {
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
          .then(response => {
            this.authorized = true
            const tunnelEndpoint = response.data.tunnel_endpoint
            const redirectUrl = new URLSearchParams(window.location.search).get('success_redirect_url') || '/tunnels/succeeded/'
            window.location.replace(`${redirectUrl}?tunnel_endpoint=${tunnelEndpoint}`)
          })
          .catch(error => {
            this.performingAuthRequest = false
            this.$swal.Reject.fire({
              title: 'Oops',
              text: error.message,
            })
          })
      }
    }
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
</style>

