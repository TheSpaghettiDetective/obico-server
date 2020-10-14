<template>

<div>
  <h4 class="text-center p-2"><i class="fas fa-lock"></i>&nbsp;OctoPrint Secure Tunnel&nbsp;<i class="fas fa-lock"></i>
  </h4>
  <div v-if="isPro" class="text-center text-muted pb-2">
    Month-To-Date Usage/Free Limit(<a href="#">?</a>): <span class="text-success">3.23MB/10MB</span>
  </div>
  <div>
    <iframe v-if="config.printerId" :src="iframeUrl()" style='width: 100%; height: 1400px; background: #FFFFFF;'></iframe>
  </div>
</div>
</template>

<script>

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
      shots: [],
      currentShot: 0,
      print: null
    }
  },
  computed: {
    isPro() {
      return this.config.isPro.toLowerCase() === 'true'
    }
  },

  mounted() {
    this.$swal.DismissableToast({
      html: '<div class="p-1">It may take long time for OctoPrint page to load as it is securely tunneled via The Spaghetti Detective server.</div><div class="p-1"><a target="_blank" href="https://www.thespaghettidetective.com/blog/2020/09/10/octoprint-tunnel-beta-testing/">Learn more about OctoPrint Tunneling\'s security and page load speed. <i class="fas fa-external-link-alt"></i></a></div>',
      customClass: {
        container: 'dark-backdrop',
      },
    }, 'octoprint-tunnel.warning')
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
