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

          <div class="webcam-main justify-center webcam-more-than-two">
            <div v-for="(webcam, index) in webcams" :key="index" ref="streamInner" class="stream-inner">
              <streaming-box
                :printer="printer"
                :webrtc="printerComm.webrtcConnections.get(webcam.name)"
                :autoplay="true"
                :webcam="webcam"
              />
            </div>
          </div>
          <div class="p-3 p-md-5">
            <p class="text-center">
              {{$t("You are viewing an awesome 3D print your friend shared specifically with you on")}}
            </p>
            <a href="https://www.obico.io/">
              <svg width="100%" class="logo-img">
                <use href="#svg-logo-full" />
              </svg>
            </a>
            <hr />
            <br /><br />
            <p class="text-center">
              {{ $syndicateText.brandName }} {{$t("lets you monitor and control your printer from anywhere, on your phone.")}}
            </p>
            <a class="btn btn-block btn-primary" href="/accounts/signup/"
              >{{ $t("Sign up for a free {brandName} account",{brandName:$syndicateText.brandName}) }}</a
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
      webcams: [],
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

          if ((this.printer?.settings?.webcams || []).length > 0) {
            const webcamsDeepCopy = JSON.parse(JSON.stringify(this.printer?.settings?.webcams)) // Probably a good idea to deep copy as we will change the objects and keep them around
            for (const webcam of webcamsDeepCopy) {
              if (this.printerComm.webrtcConnections.has(webcam.name)) {
                  continue;
              }
              this.webcams.push(webcam)
              const webrtc = WebRTCConnection(webcam.stream_mode, webcam.stream_id)
              this.printerComm.setWebRTCConnection(webcam.name, webrtc);
              // Has to be called after this.webcams.push(webcam) otherwise the callbacks won't be established properly.
              webrtc.openForShareToken(this.shareToken)
            }
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
.webcam-main
  @media (min-width: 1024px)
    height: calc(100vh - 50px - var(--gap-between-blocks)*2 - 33px)

  @media (min-width: 1024px)
    display: grid
    align-items: center
.justify-center
  @media (min-width: 1024px)
    justify-content: center
.webcam-more-than-two
  display: flex !important
  gap: 10px
</style>
