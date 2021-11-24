<template>
  <b-container>
    <b-row class="justify-content-center">
      <b-col lg="8" class="mt-3">
        <div>
          <div class="text-center">
            <svg viewBox="0 0 1965 240" width="232" height="28.34">
              <use href="#svg-navbar-brand" />
            </svg>
          </div>
          <div>
            <h4 class="text-center my-5">OctoPrint Tunnel Access Authorization</h4>
            <p class="lead"><span class="font-weight-bold">{{ appName }}</span> is requesting to access the OctoPrint Tunnel.</p>
            <p class="text-muted"><a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/" target="_blank">OctoPrint Tunnel</a> is a secure way provided by The Spaghetti Detective to securely access your OctoPrint. With the OctoPrint Tunnel, you can use {{appName}} to access your OctoPrint from anywhere.</p>

            <b-alert v-if="user && !user.is_pro" variant="warning" dismissible class="my-3" show>
              <div>
                <i class="fas fa-exclamation-triangle"></i> Tunnel usage of a free account is <a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/#why-is-the-limit-on-free-account-only-50mb" target="_blank">capped at 50MB per month</a>. You can <a href="http://app.thespaghettidetective.com/ent/pricing/" target="_blank">upgrade to The Spaghetti Detective Pro plan for 1 Starbucks a month</a> to enjoy unlimited tunnel usage.
              </div>
            </b-alert>

            <div v-if="user" class="mt-5">
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
                <button class="btn btn-primary" style="flex: 1" @click="authorize" :disabled="!printerToAuthorize">Authorize</button>
                <button class="btn btn-outline-secondary ml-2" style="flex: 1" href="#">Manage Apps</button>
              </div>
              
            </div>
            <div v-else>
              <div class="my-5">
                <a class="btn btn-primary btn-block" :href="loginUrl">Sign In </a>
                <div class="text-center pt-3 w-100">
                  <div class="font-weight-light text-muted">- OR -</div>
                  <a class="btn" :href="signupUrl">SIGN UP</a>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <p class="text-muted small mb-1">
              Security notes:
            </p>
            <ul class="text-muted small pl-4">
              <li>The app can only access the tunnel, not your The Spaghetti Detective account info such as your email address.</li>
              <li>The access remains valid until explicitly revoked. You can revoke the access by going to Preferences -> Authorized Apps.</li>
            </ul>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios'
import urls from '@lib/server_urls'
import { normalizedPrinter } from '@lib/normalizers'
import { user } from '@lib/page_context'

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
    }
  },

  created() {
    this.user = user()
    this.fetchPrinters()
    this.printerId = new URLSearchParams(window.location.search).get('printer_id')
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
    appName() {
      return new URLSearchParams(window.location.search).get('app') || 'Unknown App'
    },
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
        axios
          .post('/api/v1/tunnels/', {
            app_name: this.appName,
            printer_id: this.printerToAuthorize || this.printersToShow[0].id,
          })
          .then(response => {
            const tunnelEndpoint = response.data.tunnel_endpoint
            const redirectUrl = new URLSearchParams(window.location.search).get('success_redirect_url') || '/tunnels/succeeded/'
            window.location.replace(`${redirectUrl}?tunnel_endpoint=${tunnelEndpoint}`)
          })
          .catch(error => {
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
</style>

