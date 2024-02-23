<template>
  <div>
    <nav-bar view-name="printer_shared"></nav-bar>

    <div class="row justify-content-center">
      <b-spinner v-if="loading" class="mt-5" label="Loading..."></b-spinner>
      <div v-if="printer" class="col-sm-12 col-lg-6 printer-card">
        <div class="card">
          <div class="card-header">
            <div>{{ printer.name }}</div>
          </div>
          <streaming-box :printer="printer" :webrtc="webrtc" :autoplay="true" />
          <div class="p-3 p-md-5">
            <p class="text-center">
              You are viewing an awesome 3D print your friend shared specifically with you on
            </p>
            <a href="https://www.obico.io/">
              <svg width="100%" class="logo-img">
                <use href="#svg-logo-full" />
              </svg>
            </a>
            <hr />
            <br /><br />
            <p class="text-center">
              {{$t('brand_name')}} lets you monitor and control your printer from anywhere, on your phone.
            </p>
            <a class="btn btn-block btn-primary" href="/accounts/signup/"
              >Sign up for a free {{$t('brand_name')}} account</a
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import split from 'lodash/split'
import { normalizedPrinter } from '@src/lib/normalizers'
import urls from '@config/server-urls'
import { printerCommManager } from '@src/lib/printer-comm'
import WebRTCConnection from '@src/lib/webrtc'
import StreamingBox from '@src/components/StreamingBox'
import NavBar from '@src/components/NavBar.vue'
export default {
  name: 'SharedPrinterPage',
  components: {
    StreamingBox,
    NavBar,
  },
  data: function () {
    return {
      printer: null,
      shareToken: null,
      videoAvailable: {},
      loading: true,
      isWebrtcOpened: false,
      webrtc: WebRTCConnection(),
    }
  },
  created() {
    this.shareToken = split(window.location.pathname, '/').slice(-2, -1).pop()
    this.printerComm = printerCommManager.getOrCreatePrinterComm(
      this.shareToken,
      urls.printerSharedWebSocket(this.shareToken),
      {
        onPrinterUpdateReceived: (data) => {
          this.printer = normalizedPrinter(data, this.printer)
          this.loading = false

          if (!this.isWebrtcOpened) {
            this.webrtc.openForShareToken(this.shareToken)
            this.isWebrtcOpened = true
          }
        },
      }
    )
    this.printerComm.connect()
  },
}
</script>

<style lang="sass" scoped>
#printer-list-page
  margin-top: 1.5rem
.printer-card
  margin-bottom: 1.5rem
</style>
