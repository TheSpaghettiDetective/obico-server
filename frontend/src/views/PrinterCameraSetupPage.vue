<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <div v-if="webcamStreamShutdown">
        <loading-placeholder v-if="streamStarting" />
        <div v-else>
          <h2>{{ webcams.length }} Webcams Found</h2>
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

              <div v-if="isWebRTCCameraStreamer">
                <b-form-select
                  id="streamMode"
                  v-model="streamMode"
                  class="form-control"
                  @change="setInitStreamConfig"
                >
                  <option key="h264_copy" value="h264_copy">Stream from the MP4 source</option>
                  <option key="h264_rtsp" value="h264_rtsp">Stream from the RTSP source</option>
                </b-form-select>
                <div v-if="streamMode === 'h264_copy'">
                  <input :placeholder="'MP4 source URL'" :value="h264HttpUrl" />
                  <div>
                    You may want to turn on RTSP in OctoPrint/Crowsnest, and switch to the "RTSP
                    source" option. You will have a better streaming experience including lower
                    latency when Obico streams from RTSP source. <a href="#">Learn more</a>
                  </div>
                </div>
                <div v-if="streamMode === 'h264_rtsp'">
                  <input
                    v-if="streamMode === 'h264_rtsp'"
                    :placeholder="'RTSP Port'"
                    :value="rtspPort"
                  />
                  <div>
                    Please note that, due to an known bug, RTSP stream may fail after a few hours on
                    some Raspberry Pi devices. If this happen to you, please turn off RTSP in
                    OctoPrint/Crowsnest, come back to this page, and select "Stream from the MP4
                    source". <a href="#">Learn more</a>
                  </div>
                </div>
              </div>
              <div>
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
                    v-if="webrtc && !streamStarting"
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
              <b-button @click="$router.go(-1)">Close Setup page</b-button>
            </div>
          </div>
          <div v-else>
            <b-button @click="$router.go(-1)">Close Setup page</b-button>
          </div>
        </div>
      </div>
      <div v-else>
        <h1>Webcam Setup Wizard</h1>
        <div>
          Note: We need to shut down your current webcam streams to go through the set up process
          again.
        </div>
        <div>
          Note: Please make sure streaming in OctoPrint / Mainsail look good before continuing.
        </div>
        <div>Note: Klipper may need a restart for changes to appear here.</div>
        <b-button @click="$router.go(-1)">Go Back</b-button>
        <b-button @click="shutdownStreamButtonPressed">Continue To Webcam Setup</b-button>
      </div>
      <div>
        {{ configuredCameras.length }} camera(s) saved in Obico
        <div>
          <div v-for="webcam in configuredCameras" :key="webcam.name">
            <i class="fas fa-trash" @click="deleteWebcamConfiguration(webcam)"></i>
            {{ webcam.name }}
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
import find from 'lodash/find'

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
      webcamStreamShutdown: false,
      streamStarting: false,
      printer: null,
      webrtc: null,
      webcams: [],
      selectedWebcam: null,
      selectedWebcamData: null,
      streamMode: null,
      h264HttpUrl: null,
      rtspPort: null,
      useRTSP: false,
      isRaspi: false,
      configuredCameras: [],
    }
  },

  computed: {
    isWebRTCCameraStreamer() {
      if (!this.selectedWebcamData) return false
      return this.selectedWebcamData.service === 'webrtc-camerastreamer'
    },

    streamConfig() {
      if (!this.selectedWebcamData) return null

      const config = { mode: this.streamMode }
      if (this.streamMode === 'h264_copy') {
        config.h264_http_url = this.h264HttpUrl
      } else if (this.streamMode === 'h264_rtsp') {
        config.rtsp_port = this.rtspPort
      }

      return config
    },
  },

  watch: {
    useRTSP: function (newValue, oldValue) {
      this.webcamSelectionChanged()
    },
    isRaspi: function (newValue, oldValue) {
      this.webcamSelectionChanged()
    },
  },

  async created() {
    const printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    this.printer = await this.fetchPrinter(printerId)

    this.getConfiguredWebcams()

    this.printerComm = printerCommManager.getOrCreatePrinterComm(
      printerId,
      urls.printerWebSocket(printerId),
      {
        onPrinterUpdateReceived: null,
        onStatusReceived: null,
      }
    )
    this.printerComm.connect()
  },

  methods: {
    async fetchPrinter(printerId) {
      return axios.get(urls.printer(printerId)).then((response) => {
        return normalizedPrinter(response.data)
      })
    },

    fetchAgentWebcams() {
      const webcamFetchOctoPayload = null // TODO
      const webcamFetchMoonrakerPayload = {
        func: 'server/webcams/list',
        target: 'moonraker_api',
      }

      const webcamPayload = this.printer.isAgentMoonraker()
        ? webcamFetchMoonrakerPayload
        : webcamFetchOctoPayload

      this.printerComm.passThruToPrinter(webcamPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****2')
        } else {
          this.webcams = ret?.webcams || []
        }
      })

      const infoOctoPayload = null // TODO
      const infoMoonrakerPayload = {
        func: 'machine/system_info',
        target: 'moonraker_api',
      }
      const infoPayload = this.printer.isAgentMoonraker() ? infoMoonrakerPayload : infoOctoPayload

      this.printerComm.passThruToPrinter(infoPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****3')
        } else {
          this.isRaspi = ret.system_info.cpu_info.model.toLowerCase().includes('raspberry')
        }
      })
    },

    webcamSelectionChanged() {
      if (!this.selectedWebcam) {
        return
      }

      this.webrtc = null
      this.selectedWebcamData = this.webcams.filter((cam) => cam.name === this.selectedWebcam)[0]
      if (this.isWebRTCCameraStreamer) {
        this.streamMode = 'h264_copy'
      } else {
        this.streamMode = 'h264_recode'
      }
      this.setInitStreamConfig()
    },

    setInitStreamConfig() {
      if (this.isWebRTCCameraStreamer) {
        if (this.streamMode === 'h264_copy') {
          const streamUrl = this.webcamFullUrl(this.selectedWebcamData?.stream_url)

          // TODO: Is there a more robust way to figure out the mp4 url?
          if (streamUrl.endsWith('webrtc')) {
            this.h264HttpUrl = streamUrl.replace(/webrtc$/, 'video.mp4')
          } else {
            this.h264HttpUrl = 'http://127.0.0.1:8080/video.mp4'
          }
        } else if (this.streamMode === 'h264_rtsp') {
          this.rtspPort = 8554
        }
      }

      this.startWebcamStream()
    },

    startWebcamStream() {
      if (this.webrtc) {
        this.webrtc.disconnect()
      }
      this.streamStarting = true

      const octoPayload = null // TODO
      const moonrakerPayload = {
        func: 'start',
        target: 'webcam_streamer',
        args: [[{ name: this.selectedWebcam, config: this.streamConfig }]],
      }
      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
      this.printerComm.passThruToPrinter(
        payload,
        (err, ret) => {
          const streamId = ret?.[0]?.runtime?.stream_id
          const streamMode = ret?.[0]?.config?.mode
          if (err || streamId === undefined || streamMode === undefined) {
            console.log(err, ret)
          } else {
            this.webrtc = WebRTCConnection(streamMode, streamId)
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)

            this.streamStarting = false
          }
        },
        60
      )
    },

    shutdownStreamButtonPressed() {
      const shutdownOctoPayload = null // TODO
      const shutdownMoonrakerPayload = {
        func: 'shutdown',
        target: 'webcam_streamer',
      }

      const shutdownPayload = this.printer.isAgentMoonraker()
        ? shutdownMoonrakerPayload
        : shutdownOctoPayload

      this.printerComm.passThruToPrinter(shutdownPayload, (err, ret) => {
        if (err) {
          console.log(err, ret, '*****')
        } else {
          this.webcamStreamShutdown = true

          this.fetchAgentWebcams()
        }
      })
    },

    async saveCameraButtonPress() {
      this.$swal.Prompt.fire({
        title: 'Are you sure?',
        html: `
        <p style="text-align:center">Please verify stream is working as expected. <br/> For more information please visit <a target="_blank" href="https://www.obico.io/docs/user-guides/webcam-feed-is-not-showing/">our help docs</a>.</p>
        `,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
      }).then(async (userAction) => {
        if (userAction.isConfirmed) {
          const payload = {
            printer_id: this.printer.id,
            name: this.selectedWebcam,
            config: this.streamConfig,
          }
          const configuredCamera = find(this.configuredCameras, { name: this.selectedWebcam })
          if (configuredCamera) {
            axios.patch(urls.camera(configuredCamera.id), payload)
          } else {
            axios.post(urls.cameras(), payload)
          }
        }
      })
    },
    deleteWebcamConfiguration(webcam) {
      axios.delete(urls.newCamera(webcam.id)).then(() => {
        this.getConfiguredWebcams()
      })
    },

    getConfiguredWebcams() {
      axios.get(urls.cameras(this.printer.id)).then((resp) => {
        this.configuredCameras = resp.data
      })
    },

    webcamFullUrl(url) {
      const properSchemes = ['http://', 'https://']
      url = url.trim()
      const startsWithProperScheme = properSchemes.some((scheme) => url.startsWith(scheme))
      const startsWithSlash = url.startsWith('/')

      if (!startsWithProperScheme && !startsWithSlash) {
        url = 'http://localhost/' + url
      } else if (startsWithSlash) {
        url = 'http://localhost' + url
      }

      return url
    },
  },
}
</script>

<style lang="sass" scoped>
.streaming-wrap
  width: 600px
  height: 350px
  display: relative
  margin: 2rem 0rem 2rem 0rem

.loading-wrap
  display: flex
  flex-direction: column
  position: absolute
  justify-content: center
  align-items: center
  width: 600px
  height: 360px
  background-color: black
  z-index: 2

.webcam-data-wrap
   height: 100%
   display: flex
   flex-direction: row
   align-items: flex-start
   padding-top: 20px
   justify-content: space-around

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
