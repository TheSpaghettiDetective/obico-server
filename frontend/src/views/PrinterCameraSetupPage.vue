<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <div>
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
          <input
            :placeholder="selectedWebcamData.snapshot_url"
            :value="newSnapshotURL"
            @input="(event) => (newSnapshotURL = event.target.value)"
          />
          <input
            :placeholder="selectedWebcamData.stream_url"
            :value="newStreamURL"
            @input="(event) => (newStreamURL = event.target.value)"
          />
          <select class="custom-select">
            <option :value="null" selected disabled>Please select streaming type</option>
            <option v-for="service in services" :key="service" :value="service">
              {{ service }}
            </option>
          </select>
          <input id="checkbox0" v-model="flipHorizontal" type="checkbox" />
          <label for="checkbox0">Flip Horizontal</label>
          <input id="checkbox1" v-model="flipVertical" type="checkbox" />
          <label for="checkbox1">Flip Vertical</label>
        </div>
        <b-button @click="saveCameraButtonPress">Save Camera</b-button>
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

export default {
  name: 'PrinterCameraSetupPage',

  components: {
    PageLayout,
  },
  data: function () {
    return {
      printer: null,
      webrtc: WebRTCConnection(),
      webcams: [],
      selectedWebcam: null,
      selectedWebcamData: null,
      // camera form values
      services: [
        'mjpegstreamer',
        'mjpegstreamer-adaptive',
        'uv4l-mjpeg',
        'ipstream',
        'hlsstream',
        'jmuxer-stream',
        'webrtc-camerastreamer',
        'webrtc-janus',
        'webrtc-mediamtx',
      ],
      newStreamURL: '',
      newSnapshotURL: '',
      newServiceValue: null,
      flipHorizontal: false,
      flipVertical: true,
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
          this.selectedWebcam = this.webcams[0].name
          this.selectedWebcamData = this.webcams[0]
        }
      })
    },

    webcamSelectionChanged() {
      this.selectedWebcamData = this.webcams.filter((cam) => cam.name === this.selectedWebcam)[0]
      this.newSnapshotURL = this.selectedWebcamData.snapshot_url
      this.newStreamURL = this.selectedWebcamData.stream_url
      this.newServiceValue = this.selectedWebcamData.service
      this.flipHorizontal = this.selectedWebcamData.flip_horizontal
      this.flipVertical = this.selectedWebcamData.flip_vertical

      const octoPayload = null // TODO
      const moonrakerPayload = {
        func: 'start',
        target: 'webcam_streamer',
        args: [this.selectedWebcam],
      }
      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload

      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        console.log(err, ret)
      })
    },
    async saveCameraButtonPress() {
      if (this.printer.isAgentMoonraker()) {
        //TODO: passthru command - update moonraker api with new values
      }
      axios.post(urls.cameras(), {
        printer_id: this.printer.id,
        name: this.selectedWebcam,
      })
    },
  },
}
</script>

<style lang="sass" scoped></style>
