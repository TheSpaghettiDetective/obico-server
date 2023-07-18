<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <loading-placeholder v-if="pageLoading" />
      <div v-else>
        <select
          v-if="webcams.length > 1"
          v-model="selectedWebcam"
          class="custom-select"
          @change="webcamSelectionChanged"
        >
          <option :value="null" selected disabled>Please select a Webcam to configure</option>
          <option v-for="webcam in webcams" :key="webcam.name" :value="webcam.name">
            {{ webcam.name }}
          </option>
        </select>
        <!-- camera settings editor -->
        <div v-if="selectedWebcamData">
          <p>{{ selectedWebcamData.service }}</p>
          <p>{{ selectedWebcamData.stream_url }}</p>
          <p>{{ selectedWebcamData.snapshot_url }}</p>
          <input
            :placeholder="'RTSP Port'"
            :value="newPort"
            @input="(event) => (newPort = event.target.value)"
          />
          <b-button @click="saveCameraButtonPress">Save Camera</b-button>
        </div>
      </div>
      <div v-if="webrtc" class="streaming-wrap">
        <streaming-box
          ref="streamingBox"
          :printer="printer"
          :webrtc="webrtc"
          :autoplay="true"
          @onRotateRightClicked="
            (val) => {
              customRotationDeg = val
            }
          "
        />
      </div>
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import urls from '@config/server-urls'
import axios from 'axios'
import split from 'lodash/split'

import { normalizedPrinter } from '@src/lib/normalizers'
import WebRTCConnection from '@src/lib/webrtc'
import { printerCommManager } from '@src/lib/printer-comm'
import StreamingBox from '@src/components/StreamingBox'

export default {
  name: 'PrinterCameraSetupPage',

  components: {
    PageLayout,
    StreamingBox,
  },
  data: function () {
    return {
      pageLoading: true,
      printer: null,
      webrtc: null,
      webcams: [],
      selectedWebcam: null,
      selectedWebcamData: null,
      newPort: '',
    }
  },

  created() {
    const printerId = split(window.location.pathname, '/').slice(-3, -2).pop()

    this.fetchPrinter(printerId).then(() => {
      this.printerComm = printerCommManager.getOrCreatePrinterComm(
        printerId,
        urls.printerWebSocket(printerId),
        {
          onPrinterUpdateReceived: null,
          onStatusReceived: null,
        }
      )
      this.printerComm.connect(this.handlePageSetup)
    })
  },

  methods: {
    async fetchPrinter(printerId) {
      return axios
        .get(urls.printer(printerId))
        .then((response) => {
          this.printer = normalizedPrinter(response.data)
        })
        .catch((error) => {
          this._logError(error)
        })
    },

    async handlePageSetup() {
      const webcamFetchOctoPayload = null // TODO
      const webcamFetchMoonrakerPayload = {
        func: 'server/webcams/list',
        target: 'moonraker_api',
      }

      const shutdownOctoPayload = null // TODO
      const shutdownMoonrakerPayload = {
        func: 'shutdown',
        target: 'webcam_streamer',
        args: [[{}]],
      }
      const webcamPayload = this.printer.isAgentMoonraker()
        ? webcamFetchMoonrakerPayload
        : webcamFetchOctoPayload
      const shutdownPayload = this.printer.isAgentMoonraker()
        ? shutdownMoonrakerPayload
        : shutdownOctoPayload

      this.printerComm.passThruToPrinter(shutdownPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****')
        }
        this.pageLoading = false
      })

      this.printerComm.passThruToPrinter(webcamPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****2')
        } else {
          this.webcams = ret?.webcams || []
        }
      })
    },

    webcamSelectionChanged() {
      this.webrtc = null
      this.pageLoading = true
      this.selectedWebcamData = this.webcams.filter((cam) => cam.name === this.selectedWebcam)[0]

      const shutdownOctoPayload = null // TODO
      const shutdownMoonrakerPayload = {
        func: 'shutdown',
        target: 'webcam_streamer',
        args: [[{}]],
      }
      const shutdownPayload = this.printer.isAgentMoonraker()
        ? shutdownMoonrakerPayload
        : shutdownOctoPayload

      this.printerComm.passThruToPrinter(shutdownPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****')
        }
        const octoPayload = null // TODO
        const moonrakerPayload = {
          func: 'start',
          target: 'webcam_streamer',
          args: [[{ name: this.selectedWebcam, config: { mode: 'h264-recode' } }]],
        }
        const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
        // TODO: update stream with selected camera settings
        this.printerComm.passThruToPrinter(payload, (err, ret) => {
          if (err) {
            console.log(err, ret)
          } else {
            this.webrtc = WebRTCConnection()
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)
            this.$refs?.streamingBox?.restartStream()
          }
          this.pageLoading = false
        })
      })
    },
    async saveCameraButtonPress() {
      axios.post(urls.cameras(), {
        printer_id: this.printer.id,
        name: this.selectedWebcam,
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.streaming-wrap
  width: 500px
  height: 500px
</style>
