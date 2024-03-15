<template>
  <div class="px-2">
    <div class="title-pic">
      <img class="pic-item" :src="require('@static/img/webpage-multiple.svg')" />
      <div class="pic-item">
        <i class="fas fa-ellipsis-h fa-2x"></i>
        <i class="fas fa-ellipsis-h fa-2x"></i>
      </div>
      <img class="pic-item" :src="require('@static/img/printer.png')" />
    </div>
    <div class="my-4">
      <p>The {{ $t('brand_name') }} app needs to make sure you have access to selected printer.</p>
      <p>
        When you press "Link Now" button below, a new browser window will pop up to finish a
        handshake with this printer.
      </p>
    </div>
    <div>
      <div class="row my-2">
        <div class="col-sm-6">
          <button
            class="btn btn-block btn-primary mt-2"
            :disabled="linking"
            @click="autoLinkPrinter"
          >
            <b-spinner v-if="linking" small></b-spinner>Link Now&nbsp;<i
              class="fas fa-external-link-alt"
            ></i>
          </button>
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
  props: {
    discoveredPrinter: {
      type: Object,
      required: true,
    },
    switchToManualLinking: {
      type: Function,
      required: true,
    },
    secretObtained: {
      type: Function,
      required: true,
    },
  },
  data() {
    return {
      linking: false,
    }
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

      this.obicoDiscoveryPopup = window.open(
        this.destUrl(),
        '_blank',
        'toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=no,width=500,height=100'
      )

      if (!this.obicoDiscoveryPopup) {
        this.cancel()
        this.$swal.Prompt.fire({
          icon: 'error',
          title: 'Oops!',
          html: '<p>Handshake failed because the pop-up was blcoked.</p><p>Please unblock the pop-up in your browser and try it again.</p>',
          confirmButtonText: 'Okay!',
          showCancelButton: true,
          cancelButtonText: 'Switch to Manual Setup',
        }).then((result) => {
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
            html: `<p>Please make sure:</p>
              <ul>
                <li>The OctoPrint you want to link is at ${this.discoveredPrinter.host_or_ip}:${this.discoveredPrinter.port}, and it's connected to the same local network as your computer/phone.</li>
                <li>The version of plugin is 1.8.0 or above.</li>
              </ul>`,
            confirmButtonText: 'Okay!',
            showCancelButton: true,
            cancelButtonText: 'Switch to Manual Setup',
          }).then((result) => {
            if (result.isDismissed && result.dismiss === 'cancel') {
              this.switchToManualLinking()
            }
          })
        }
      }, 5000)
    },

    destUrl() {
      const pluginName = this.discoveredPrinter.agent ? 'obico' : 'thespaghettidetective'
      return `http://${this.discoveredPrinter.host_or_ip}:${
        this.discoveredPrinter.port || '80'
      }/plugin/${pluginName}/grab-discovery-secret?device_id=${this.discoveredPrinter.device_id}`
    },

    switchToManual() {
      this.cancel()
      this.switchToManualLinking()
    },

    closeDiscoveryPopup() {
      if (this.obicoDiscoveryPopup) {
        this.obicoDiscoveryPopup.close()
        this.obicoDiscoveryPopup = null
      }
    },

    gotWindowMessage(ev) {
      const data = { ...(ev?.data || {}) }
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
    },
  },
}
</script>

<style lang="sass" scoped>

.title-pic
  display: flex
  margin: 1.5rem 0
  justify-content: center

  .pic-item
    height: 3rem
    margin: 0 0.5rem

  img
    filter: grayscale(100%)
  i
    color: #888888
</style>
