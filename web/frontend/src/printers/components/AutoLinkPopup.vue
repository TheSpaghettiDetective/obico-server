<template>
  <div class="px-2">
    <div class="my-4">
      <p>The Spaghetti Detective needs to make sure you have access to this OctoPrint.</p>
      <p>When you press "Link Now" button below, a new browser window will pop up to finish a handshake with this OctoPrint.</p>
    </div>
    <div>
    <div class="row my-2">
      <div class="col-sm-6">
        <button class="btn btn-block btn-primary mt-2" :disabled="linking" @click="autoLinkPrinter"><b-spinner v-if="linking" small></b-spinner>Link Now</button>
      </div>
      <div class="col-sm-6">
        <button class="btn btn-block btn-secondary mt-2" @click="cancel">Cancel</button>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AutoLinkPopup',
  data() {
    return {
      linking: false,
    }
  },
  props: {
    discoveredPrinter: {
      type: Object,
      required: true
    },
    switchToManualLinking: {
      type: Function,
      required: true
    },
    secretObtained: {
      type: Function,
      required: true
    },
  },

  mounted() {
    window.addEventListener('message', this.gotWindowMessage)
  },

  beforeDestroy() {
    window.removeEventListener('message', this.gotWindowMessage)
  },

  methods: {
    autoLinkPrinter() {
      this.linking = true
      this.gotSecret = null

      this.tsdDiscoveryPopup = window.open(
        this.destUrl(),
        '_blank',
        'toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=no,width=500,height=100'
      )

      if (!this.tsdDiscoveryPopup) {
        this.cancel()
        this.$swal.Prompt.fire({
          icon: 'error',
          title: 'Oops!',
          html:
            '<p>Handshake failed because the pop-up was blcoked.</p><p>Please unblock the pop-up in your browser and try it again.</p>',
          confirmButtonText: 'Okay!',
          showCancelButton: true,
          cancelButtonText: 'Switch to Manual Setup'
        }).then(result => {
          if (result.isDismissed && result.dismiss === 'cancel') {
            this.switchToManualLinking()
          }
        })
        return
      }

      setTimeout(() => {
        this.closeDiscoveryPopup()

        if (!this.gotSecret) {
          this.cancel()
          this.$swal.Prompt.fire({
            icon: 'error',
            title: 'Handshake failed!',
            html:
              `<p>Please make sure:</p>
              <ul>
                <li>The OctoPrint you want to link is at ${this.discoveredPrinter.host_or_ip}:${this.discoveredPrinter.port}, and it's connected to the same local network as your computer/phone.</li>
                <li>The version of plugin is 1.8.0 or above.</li>
              </ul>`,
            confirmButtonText: 'Okay!',
            showCancelButton: true,
            cancelButtonText: 'Switch to Manual Setup'
          }).then(result => {
            if (result.isDismissed && result.dismiss === 'cancel') {
              this.switchToManualLinking()
            }
          })
        }
      }, 5000)
    },

    destUrl() {
      return `http://${this.discoveredPrinter.host_or_ip}:${this.discoveredPrinter.port || '80'}/plugin/thespaghettidetective/grab-discovery-secret?device_id=${this.discoveredPrinter.device_id}`
    },

    switchToManual() {
      this.cancel()
      this.switchToManualLinking()
    },

    closeDiscoveryPopup() {
      if (this.tsdDiscoveryPopup) {
        this.tsdDiscoveryPopup.close()
        this.tsdDiscoveryPopup = null
      }
    },

    gotWindowMessage(ev) {
      const data = {...(ev?.data || {})}
      if (this.gotSecret || !this.discoveredPrinter.device_id || !data.device_secret) {
        console.log('Ignored message', ev)
        return
      }

      this.gotSecret = data
      this.secretObtained(this.discoveredPrinter.device_id, data.device_secret)
      this.cancel()
    },

    cancel() {
      this.closeDiscoveryPopup()
      this.$swal.close()
    }
  },
}
</script>
