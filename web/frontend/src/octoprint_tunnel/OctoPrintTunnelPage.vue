<template>

<div>
  <h4 class="text-center p-2"><i class="fas fa-lock"></i>&nbsp;OctoPrint Secure Tunnel&nbsp;<i class="fas fa-lock"></i>
  </h4>
  <div v-if="isPro" class="text-center text-muted pb-2">
    Month-To-Date Usage/Free Limit(<a href="#">?</a>): <span :class="usageClass">{{ usageMTD }}/20MB</span>
  </div>
  <div>
    <iframe v-if="config.printerId" :src="iframeUrl()" style='width: 100%; height: 1400px; background: #FFFFFF;'></iframe>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import filesize from 'filesize'
import apis from '@lib/apis'

const USAGE_CAP = 20 * 1024 * 1024

export default {
  name: 'OctoPrintTunnelPage',
  props: {
    config: {
      default: () => {},
      type: Object
    }
  },
  data: function() {
    return {
      bytesMTD: null,
    }
  },

  computed: {
    isPro() {
      return this.config.isPro.toLowerCase() === 'true'
    },

    usageClass() {
      return {
        'text-success': this.bytesMTD < USAGE_CAP * 0.8,
        'text-warning': this.bytesMTD >= USAGE_CAP * 0.8 && this.bytesMTD < USAGE_CAP,
        'text-danger': this.bytesMTD >= USAGE_CAP
      }
    },

    usageMTD() {
      return filesize(this.bytesMTD)
    }
  },

  mounted() {
    this.$swal.DismissableToast({
        html: '<div class="p-1">It may take long time for OctoPrint page to load as it is securely tunneled via The Spaghetti Detective server.</div><div class="p-1"><a target="_blank" href="https://www.thespaghettidetective.com/blog/2020/09/10/octoprint-tunnel-beta-testing/">Learn more about OctoPrint Tunneling\'s security and page load speed. <i class="fas fa-external-link-alt"></i></a></div>',
        customClass: {
          container: 'dark-backdrop',
        },
      },
      'octoprint-tunnel.warning')

    const self = this
    const fetchUsage = () => {
      axios
        .get(apis.tunnelUsage())
        .then((resp) => {
          self.bytesMTD = resp.data.total
        })
    }
    setInterval(fetchUsage, 15*1000)
    fetchUsage()
  },

  methods: {
    iframeUrl() {
      return `/octoprint/${this.config.printerId}/`
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"
</style>
