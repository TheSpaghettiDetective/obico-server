<template>
  <div>
    <div v-if="!isPro" class="floating-panel text-center pb-2">
      <div class="text-muted">Month-To-Date Usage/Free Limit(<a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users">?</a>)</div>
      <div :class="usageClass">{{ usageMTD }}/{{ humanizedUsageCap }}</div>
      <div v-if="overage">Your month-to-date tunneling usage is over the Free plan limit. <a type="button" class="btn btn-sm btn-primary" href="/ent_pub/pricing/">Get Unlimited Tunneling</a></div>
    </div>
    <div>
      <iframe v-if="printerId" :src="iframeUrl() + '#temp'" class="tunnel-iframe"></iframe>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import split from 'lodash/split'
import filesize from 'filesize'
import urls from '@lib/server_urls'
import { user } from '@lib/page_context'
import { isLocalStorageSupported } from '@common/utils'

export default {
  name: 'OctoPrintTunnelPage',

  components: {},

  data: function() {
    return {
      bytesMTD: null,
      usageCap: null,
      isPro: true,
      printerId: null,
    }
  },

  computed: {
    usageClass() {
      return {
        'text-success': this.bytesMTD < this.usageCap * 0.8,
        'text-warning': this.bytesMTD >= this.usageCap * 0.8 && this.bytesMTD < this.usageCap,
        'text-danger': this.bytesMTD >= this.usageCap
      }
    },
    usageMTD() {
      return filesize(this.bytesMTD)
    },
    humanizedUsageCap() {
      return filesize(this.usageCap)
    },
    overage() {
      return this.bytesMTD >= this.usageCap
    },
  },

  created() {
    this.isPro = user().is_pro
    this.printerId = split(window.location.pathname, '/').slice(-2, -1).pop()
  },

  mounted() {
    const skipWarning = isLocalStorageSupported() ? localStorage.getItem('skip-tunneling-warning') : null
    if (skipWarning !== 'yes') {
      this.$swal.Prompt.fire({
        html: `
          <h4 class="text-center p-2">
            <svg class="menu-icon" fill="currentColor" viewBox="0 0 346.26 368.59" style="height: 1.1em;margin-right: 0.75em;">
              <use href="#svg-octoprint-tunneling" />
            </svg>
            OctoPrint Secure Tunnel
          </h4>
          <div class="p-1">
            It may take long time for OctoPrint page to load as it is securely tunneled via The Spaghetti Detective server.
          </div>
          <div class="p-1">
            <a target="_blank" href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users">
            Learn more about OctoPrint Tunneling's security and page load speed.
            <i class="fas fa-external-link-alt"></i>
          </a>
        </div>
        `,
        input: 'checkbox',
        inputPlaceholder: 'Don\'t show again',
      },
      'octoprint-tunnel.warning').then((result) => {
        if (result.isConfirmed) {
          if (result.value && isLocalStorageSupported()) {
            localStorage.setItem('skip-tunneling-warning', 'yes')
          }
        }
      })
    }

    const self = this
    const fetchUsage = () => {
      axios
        .get(urls.tunnelUsage())
        .then((resp) => {
          self.bytesMTD = resp.data.total
          self.usageCap = resp.data.monthly_cap
        })
    }
    setInterval(fetchUsage, 15*1000)
    setTimeout(fetchUsage, 4000)
  },

  methods: {
    iframeUrl() {
      return `/octoprint/${this.printerId}/`
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.tunnel-iframe
    width: 100%
    height: 100vh
    background: var(--color-background)
    position: absolute
    top: 0
    left: 0

.floating-panel
  position: fixed
  bottom: 15px
  right: 15px
  box-shadow: 2px 2px 10px rgba(0,0,0,.3)
  background-color: var(--color-surface-primary)
  padding: 10px
  max-width: 300px
  z-index: 10
</style>

<style lang="sass">
@media (pointer:none), (pointer:coarse)
  .swal2-popup
    transform: scale(1.5)
  .floating-panel
    transform: scale(2)
    transform-origin: right bottom
</style>
