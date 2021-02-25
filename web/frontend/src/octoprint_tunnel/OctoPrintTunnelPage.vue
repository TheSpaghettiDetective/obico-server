<template>

<div>
  <h4 class="text-center p-2"><img style="height: 1.1em;margin-right: 0.75em;" :src="require('@static/img/octoprint-tunnel.png')" />OctoPrint Secure Tunnel
  </h4>
  <div v-if="!isPro" class="text-center pb-2">
    <span class="text-muted">Month-To-Date Usage/Free Limit(<a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users">?</a>):</span> <span :class="usageClass">{{ usageMTD }}/{{ humanizedUsageCap }}</span>
    <div v-if="overage">Your month-to-date tunneling usage is over the Free plan limit. Upgrade to the Pro plan to <a type="button" class="btn btn-sm btn-primary" href="/ent/pricing/">Get Unlimited Usage</a></div>
  </div>
  <div>
    <iframe v-if="printerId" :src="iframeUrl()" style='width: 100%; height: 1400px; background: #FFFFFF;'></iframe>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import filesize from 'filesize'
import urls from '@lib/server_urls'

export default {
  name: 'OctoPrintTunnelPage',
  props: {
    printerId: {
      type: Number
    },
    isPro: {
      type: Boolean
    },
    usageCap: {
      type: Number
    },
  },
  data: function() {
    return {
      bytesMTD: null,
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

  mounted() {
    this.$swal.DismissableToast({
        html: '<div class="p-1">It may take long time for OctoPrint page to load as it is securely tunneled via The Spaghetti Detective server.</div><div class="p-1"><a target="_blank" href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/#is-octoprint-tunneling-secure">Learn more about OctoPrint Tunneling\'s security and page load speed. <i class="fas fa-external-link-alt"></i></a></div>',
        customClass: {
          container: 'dark-backdrop',
        },
      },
      'octoprint-tunnel.warning')

    const self = this
    const fetchUsage = () => {
      axios
        .get(urls.tunnelUsage())
        .then((resp) => {
          self.bytesMTD = resp.data.total
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
</style>
