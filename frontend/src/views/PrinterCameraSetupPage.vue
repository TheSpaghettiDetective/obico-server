<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <loading-placeholder v-if="pageLoading" />
      <div v-else>
        <b-form-select
          v-if="webcams.length > 1"
          v-model="selectedWebcam"
          class="form-control"
          @change="webcamSelectionChanged"
        >
          <option :value="null" selected disabled>Please select a Webcam to configure</option>
          <option v-for="webcam in webcams" :key="webcam.name" :value="webcam.name">
            {{ webcam.name }}
          </option>
        </b-form-select>
        <!-- camera settings editor -->
        <div v-if="selectedWebcamData" class="webcam-data-wrap">
          <div class="content-column">
            <p>Stream URL: {{ selectedWebcamData.stream_url ?? '' }}</p>
            <p>Snapshot URL: {{ selectedWebcamData.snapshot_url ?? '' }}</p>
            <p>Target FPS: {{ selectedWebcamData.target_fps ?? '' }}</p>
            <div v-if="selectedWebcamData?.service.includes('webrtc')">
              <b-form-group class="m-0">
                <b-form-checkbox v-model="useRTSP" size="md">RTSP Enabled</b-form-checkbox>
              </b-form-group>
              <input
                :placeholder="'RTSP Port'"
                :value="newPort"
                @input="(event) => (newPort = event.target.value)"
              />
            </div>
            <div v-else>
              <b-form-group class="m-0">
                <b-form-checkbox v-model="isRaspi" size="md"
                  >Raspberry Pi Device <small>(Unsure? Leave as is.)</small></b-form-checkbox
                >
              </b-form-group>
            </div>
            <b-button @click="saveCameraButtonPress">Save Camera</b-button>
          </div>
          <div class="content-column">
            <small>*Please allow 10-15s between each modification for new stream to load.</small>
            <div class="streaming-wrap">
              <div v-if="!webrtc" class="loading-wrap">
                <loading-placeholder />
                <small class="creating-stream-text">Creating Stream...</small>
              </div>
              <div v-else>
                <streaming-box
                  ref="streamingBox"
                  :printer="printer"
                  :webrtc="webrtc"
                  :autoplay="true"
                  :show-settings-icon="false"
                  @onRotateRightClicked="
                    (val) => {
                      customRotationDeg = val
                    }
                  "
                />
              </div>
            </div>
          </div>
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
      pageLoading: true,
      printer: null,
      webrtc: null,
      webcams: [],
      selectedWebcam: null,
      selectedWebcamData: null,
      newPort: '8080',
      useRTSP: false,
      isRaspi: false,
    }
  },

  watch: {
    useRTSP: function (newValue, oldValue) {
      this.webcamSelectionChanged()
    },
    isRaspi: function (newValue, oldValue) {
      this.webcamSelectionChanged()
    },
    newPort: function (newValue, oldValue) {
      this.webcamSelectionChanged()
    },
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

      const infoOctoPayload = null // TODO
      const infoMoonrakerPayload = {
        func: 'machine/system_info',
        target: 'moonraker_api',
      }
      const webcamPayload = this.printer.isAgentMoonraker()
        ? webcamFetchMoonrakerPayload
        : webcamFetchOctoPayload
      const shutdownPayload = this.printer.isAgentMoonraker()
        ? shutdownMoonrakerPayload
        : shutdownOctoPayload
      const infoPayload = this.printer.isAgentMoonraker() ? infoMoonrakerPayload : infoOctoPayload

      this.printerComm.passThruToPrinter(shutdownPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****')
        }
      })

      this.printerComm.passThruToPrinter(webcamPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****2')
        } else {
          this.webcams = ret?.webcams || []
        }
      })

      this.printerComm.passThruToPrinter(infoPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****3')
        } else {
          this.isRaspi = ret.system_info.cpu_info.model.toLowerCase().includes('raspberry')
          this.pageLoading = false
        }
      })
    },

    webcamSelectionChanged() {
      this.webrtc = null
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
          args: [[{ name: this.selectedWebcam, config: { mode: this.getModeValue() } }]],
        }
        const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
        this.printerComm.passThruToPrinter(payload, (err, ret) => {
          if (err) {
            console.log(err, ret)
          } else {
            this.webrtc = WebRTCConnection()
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)
            this.$refs?.streamingBox?.restartStream()
          }
        })
      })
    },
    async saveCameraButtonPress() {
      axios.get(urls.cameras(this.printer.id)).then((resp) => {
        if (resp.data.length > 0) {
          axios
            .put(urls.newCamera(resp.data[0].id), {
              printer_id: this.printer.id,
              name: this.selectedWebcam,
              config: {
                mode: this.getModeValue(),
                h264_http_url: `http://127.0.0.1:${this.newPort}/video.mp4`,
              },
            })
            .then((resp) => console.log(resp))
        } else {
          axios.post(urls.newCamera(), {
            printer_id: this.printer.id,
            name: this.selectedWebcam,
            config: {
              mode: this.getModeValue(),
              h264_http_url: `http://127.0.0.1:${this.newPort}/video.mp4`,
            },
          })
        }
      })
    },
    getModeValue() {
      if (!this.selectedWebcamData) return
      if (this.selectedWebcamData.service.includes('mjpeg')) {
        if (this.isRaspi) {
          return 'h264-recode'
        } else {
          return 'mjpeg-webrtc'
        }
      } else if (this.selectedWebcamData.service.includes('webrtc')) {
        if (this.useRTSP) {
          return 'h264-rtsp'
        } else {
          return 'h264-copy'
        }
      } else return 'h264-recode'
    },
  },
}
</script>

<style lang="sass" scoped>
.streaming-wrap
  width: 500px
  height: 300px
  display: relative

.loading-wrap
  display: flex
  flex-direction: column
  position: absolute
  justify-content: center
  align-items: center
  width: 500px
  height: 300px
  background-color: black
  z-index: 2

.webcam-data-wrap
   width: 100wv
   height: 100%
   display: flex
   flex-direction: row
   align-items: flex-start
   padding-top: 20px
   justify-content: space-between

.content-column
   display: flex
   flex-direction: column
   flex-wrap: wrap
   max-width: 50%

.creating-stream-text
  position: absolute
  bottom: 0
  padding-bottom: 10px
</style>
