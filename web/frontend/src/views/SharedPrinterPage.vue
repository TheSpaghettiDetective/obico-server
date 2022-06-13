<template>
  <div>
    <navbar view-name="printer_shared"></navbar>

    <div class="row justify-content-center">
      <b-spinner v-if="loading" class="mt-5" label="Loading..."></b-spinner>
      <div v-if="printer"
        class="col-sm-12 col-lg-6 printer-card"
      >
        <div class="card">
          <div class="card-header">
            <div>{{ printer.name }}</div>
          </div>
          <streaming-box :printer="printer" :webrtc="webrtc" />
          <div class="p-3 p-md-5">
            <p class="text-center">You are viewing an awesome 3D print your friend shared specifically with you on</p>
            <a href="https://www.obico.io/">
              <svg width="100%" class="logo-img">
                <use href="#svg-logo-full" />
              </svg>
            </a>
            <hr />
            <br /><br />
            <a class="btn btn-block btn-primary" href="/accounts/signup/">Get OctoPrint remote monitoring/access for FREE</a>
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
import PrinterComm from '@src/lib/printer_comm'
import WebRTCConnection from '@src/lib/webrtc'
import StreamingBox from '@src/components/StreamingBox'
import Navbar from '@src/components/Navbar.vue'
export default {
  name: 'SharedPrinterPage',
  components: {
    StreamingBox,
    Navbar,
  },
  created(){
    this.shareToken = split(window.location.pathname, '/').slice(-2, -1).pop()
    this.printerComm = PrinterComm(
      this.shareToken,
      urls.printerSharedWebSocket(this.shareToken),
      (data) => {
        this.printer = normalizedPrinter(data, this.printer)
        this.loading = false
      }
    )
    this.printerComm.connect()
    this.webrtc.openForShareToken(this.shareToken)
  },
  data: function() {
    return {
      printer: null,
      shareToken: null,
      videoAvailable: {},
      loading: true,
      webrtc: WebRTCConnection(true),
    }
  },
}
</script>

<style lang="sass" scoped>
#printer-list-page
  margin-top: 1.5rem
.printer-card
  margin-bottom: 1.5rem
</style>
