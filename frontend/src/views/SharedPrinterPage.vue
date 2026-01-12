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

        <b-card-text v-if="webcams.length || printer?.pic?.img_url" class="px-0 py-0 content d-inline-block" style="width: 100%;">
            <b-row>
                <b-col class="pb-0" style="position: relative">
                  <b-container fluid class="p-0">
                    <b-row no-gutters>
                      <b-col v-if="webcams.length === 0 && printer?.pic?.img_url" :key="printer?.pic?.img_url" :cols="12">
                        <div class="d-flex justify-content-center webcamBackground">
                          <streaming-box
                            :printer="printer"
                            :autoplay="true"
                            :stickyStreamingSrc="'IMAGE'"
                          />
                        </div>
                      </b-col>
                      <b-col v-for="(webcam, index) in webcams" :key="index" :cols="webcams.length > 1 ? 6 : 12">
                        <div class="d-flex justify-content-center webcamBackground">
                          <streaming-box
                            :printer="printer"
                            :webrtc="printerComm.webrtcConnections.get(webcam.name)"
                            :autoplay="true"
                            :webcam="webcam"
                          />
                        </div>
                      </b-col>
                    </b-row>
                  </b-container>
              </b-col>
            </b-row>
        </b-card-text>
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
.webcamBackground
    position: relative
    background: #000

#printer-list-page
  margin-top: 1.5rem
.printer-card
  margin-bottom: 1.25rem
</style>
