<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <loading-placeholder v-if="!printer" />
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
        <div class="streaming-wrap">
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
      printer: null,
      webrtc: WebRTCConnection(),
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
      this.printerComm.connect(this.fetchWebcamSettings)

      this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
      this.printerComm.setWebRTC(this.webrtc)
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

    async fetchWebcamSettings() {
      const octoPayload = null // TODO
      const moonrakerPayload = {
        func: 'server/webcams/list',
        target: 'moonraker_api',
      }

      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        } else {
          this.webcams = ret?.webcams || []
        }
      })
    },

    webcamSelectionChanged() {
      this.selectedWebcamData = this.webcams.filter((cam) => cam.name === this.selectedWebcam)[0]

      const octoPayload = null // TODO
      const moonrakerPayload = {
        func: 'start',
        target: 'webcam_streamer',
        args: [[{ name: this.selectedWebcam, config: { mode: 'h264-recode' } }]],
      }
      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload

      this.$refs.streamingBox.restartStream()

      // TODO: update stream with selected camera settings
      // this.printerComm.passThruToPrinter(payload, (err, ret) => {
      //   console.log(err, ret)
      // })
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
