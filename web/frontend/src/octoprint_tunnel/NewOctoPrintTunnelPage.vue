<template>
  <b-container>
    <b-row class="justify-content-center">
      <b-col lg="8" class="mt-3">
        <b-container fluid>
          <b-row>
            <b-col class="text-center">
              <svg viewBox="0 0 1965 240" width="232" height="28.34">
                <use href="#svg-navbar-brand" />
              </svg>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <h4 class="text-center mt-5 mb-3">OctoPrint Tunnel Access Authorization</h4>
              <p class="font-weight-bold">{{ appName }} is requesting to access the tunnel so that it can connect to your OctoPrint from anywhere.</p>
              <p>OctoPrint Tunnel is a secure way provided by The Spaghetti Detective to securely access your OctoPrint even if you are not on the same local network as your OctoPrint is.</p>

              <b-alert v-if="user && !user.is_pro" variant="warning" class="mb-3" show>Since you are on the free account, yor tunnel usage will be capped at 50MB per month. The quota is reset on the 1st day of each month. You can upgrade to the Pro plan to enjoy unlimited tunnel usage.</b-alert>

              <div v-if="user">
                <p class="font-weight-bold">Make sure you trust {{ appName }} before you authorize this request.</p>
                <h5 v-if="printersToShow.length === 0">You have 0 active printers</h5>
                <h5 v-else-if="printersToShow.length === 1" class="font-weight-bold">{{ printersToShow[0].name }}</h5>
                <select v-else-if="printersToShow.length > 1" v-model="printerToAuthorize" class="custom-select">
                  <option
                    v-for="printer in printersToShow"
                    :key="printer.id"
                    :value="printer.id"
                  >
                    {{ printer.name }}
                  </option>
                </select>
                <div v-if="printersToShow.length" class="d-flex mt-3 mb-3">
                  <button class="btn btn-primary" style="flex: 1" @click="authorize">Authorize</button>
                  <button class="btn btn-secondary ml-2" style="flex: 1">Cancel</button>
                </div>
                <a href="#">Manage authorized apps</a>
              </div>
              <div v-else>
                <div>
                  Please&nbsp;<a class="link" :href="loginUrl">sign in to your The Spaghetti Detective account</a>&nbsp; to continue, or &nbsp;<a class="link" :href="signupUrl">sign up for an free account</a>&nbsp; if you don't have one.
                </div>
              </div>
            </b-col>
          </b-row>
          <b-row class="mt-4">
            <b-col>
              <p class="text-muted small mb-1">
                Security notes:
              </p>
              <ul class="text-muted small pl-4">
                <li>The app can only access the tunnel, not your account info such as your email address.</li>
                <li>The access remains valid until explicitly revoked. You can revoke the access by going to Preferences -> Authorized Apps.</li>
              </ul>
            </b-col>
          </b-row>
        </b-container>
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

  props: {
    appName: {
      type: String,
      required: true,
    },
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

    console.log(window.location)
  },

  computed: {
    printersToShow() {
      return this.printerId ? this.printers.filter((printer) => printer.id == this.printerId) : this.printers
    },
    loginUrl() {
      return `/accounts/login/?hide_navbar=true&next=${window.location.pathname}${window.location.search}`
    },
    signupUrl() {
      return `/accounts/signup/?hide_navbar=true&next=${window.location.pathname}${window.location.search}`
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
            window.location.replace(`/tunnels/succeeded/?tunnel_endpoint=${tunnelEndpoint}`)
          })
          .catch(error => {
            alert(error.message)
            console.log(error)
          })
      }
    }
  },
}
</script>

<style lang="sass">
body
  padding-bottom: 0
</style>

