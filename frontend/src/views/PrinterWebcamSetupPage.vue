<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <div>
        <select
          v-if="webcams.length > 1"
          v-model="selectedWebcam"
          @change="webcamSelectionChanged"
          class="custom-select"
        >
          <option :value="null" selected disabled>Please select a Webcam to configure</option>
          <option v-for="webcam in webcams" :key="webcam.name" :value="webcam.name">
            {{ webcam.name }}
          </option>
        </select>
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
  name: 'PrinterWebcamSetupPage',

  components: {
    PageLayout,
  },
  data: function () {
    return {
      printer: null,
      webrtc: WebRTCConnection(),
      webcams: [],
      selectedWebcam: null,
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
  },
}
</script>

<style lang="sass" scoped></style>
