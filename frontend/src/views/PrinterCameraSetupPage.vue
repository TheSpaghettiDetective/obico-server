<template>
  <page-layout>
    <!-- Page content -->
    <template #content>
      <div v-if="errorMessage">
        <i class="fas fa-times-circle fa-2x"></i>
        <p>
          {{ errorMessage }}
        </p>
      </div>
      <div v-else-if="actionMessage">
        <loading-placeholder />
        <p>
          {{ actionMessage }}
        </p>
      </div>
      <div v-else>
        <div v-if="webcams === null">
          <h1>Webcam Setup Wizard</h1>
          <div>
            We need to shut down your current webcam stream(s) in the Obico app to go through the
            set up process again.
          </div>
          <div>
            Note: Your webcam stream(s) in {{ printer.agentDisplayName() }} won't be affected.
          </div>
          <b-button @click="$router.go(-1)">Go Back</b-button>
          <b-button @click="shutdownStreamButtonPressed">Continue To Webcam Setup</b-button>
          <p />

          <div>
            {{ configuredCameras.length }} camera(s) saved in Obico
            <div>
              <div v-for="webcam in configuredCameras" :key="webcam.name">
                <i class="fas fa-trash" @click="deleteWebcamConfiguration(webcam)"></i>
                {{ webcam.name }}
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <div v-if="webcams.length > 0">
            <h3>{{ webcams.length }} Webcams Found</h3>
            <b-form-select
              v-model="selectedWebcam"
              class="form-control"
              @change="webcamSelectionChanged"
            >
              <option :value="null" selected disabled>Please select a Webcam to configure</option>
              <option v-for="webcam in webcams" :key="webcam.name" :value="webcam.name">
                {{ webcam.name }}
              </option>
            </b-form-select>
          </div>
          <div v-else>
            <i class="fas fa-times-circle fa-2x"></i>
            <h3>No webcams are found for your {{ printer.agentDisplayName() }} printer.</h3>
            <div>
              Please set them up in {{ agentUIDisplayName }} first. Once webcams are properly
              working in {{ agentUIDisplayName }}, come back here and try it again.
            </div>
            <div>For details, please refer to <a href="#">the Obico webcam setup guide</a></div>
          </div>
          <!-- camera settings editor -->
          <div v-if="selectedWebcamData" class="webcam-data-wrap">
            <div class="content-column">
              <b-card class="mb-3">
                <template #header>
                  <b-button variant="link">
                    Webcam details. Default to be collapsed
                    <i class="fas fa-chevron-up"></i>
                  </b-button>
                </template>
                <b-collapse visible>
                  <b-card-body>
                    <p>Stream URL: {{ selectedWebcamData.stream_url ?? '' }}</p>
                    <p>Snapshot URL: {{ selectedWebcamData.snapshot_url ?? '' }}</p>
                    <p>Target FPS: {{ selectedWebcamData.target_fps ?? '' }}</p>
                    <p>Probably more...</p>
                  </b-card-body>
                </b-collapse>
              </b-card>
              <hr />
              <h3>Orientation</h3>
              <div>
                <label for="flipHCheckbox">Flip Horizontally:</label>
                <input
                  id="flipHCheckbox"
                  v-model="selectedWebcamData.flip_horizontal"
                  disabled="true"
                  type="checkbox"
                />
              </div>
              <div>
                <label for="flipVCheckbox">Flip Horizontally:</label>
                <input
                  id="flipVCheckbox"
                  v-model="selectedWebcamData.flip_vertical"
                  disabled="true"
                  type="checkbox"
                />
              </div>
              <div>
                <label for="rotationInput">Rotation:</label>
                <input
                  id="rotationInput"
                  type="text"
                  :value="selectedWebcamData.rotation"
                  disabled
                />
              </div>
              <p class="text-warning">
                The settings above are retrieved from {{ agentUIDisplayName }}. If they are not
                correct, change them in {{ agentUIDisplayName }}. Don't forget to restart the system
                afterward as your change may not take effect until a complete restart.
              </p>
              <hr />
              <div v-if="isWebRTCCameraStreamer">
                <h3>Source</h3>
                <div>
                  It looks like you are using WebRTC to stream your webcam. Good call! WebRTC is
                  much more efficient than the legacy MJPEG format and we have been using it in the
                  Obico app since day one!
                </div>
                <div>
                  Your WebRTC stream may provide 2 sources that we can use: MP4 and RTSP. RTSP is a
                  more advanced one as it has much smaller latency. But it's also new and hence may
                  not be stable.
                </div>
                <div>
                  You can try both sources to see which one works for you.
                  <a href="#">Learn more.</a>
                </div>
                <br />

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
                  You are currently using the MP4 source. Consider turning on RTSP in
                  {{ newCameraStackDisplayName }}, and switch to the "Stream from the RTSP source"
                  option. You will have a better streaming experience including lower latency when
                  Obico streams from RTSP source. <a href="#">Learn more.</a>
                </div>
                <div v-if="streamMode === 'h264_rtsp'">
                  You are currently using the RTSP source. Please note that, due to an known bug,
                  RTSP stream may fail <i>after a few hours</i> on some Raspberry Pi devices. If
                  this happen to you, please turn off RTSP in {{ newCameraStackDisplayName }}, come
                  back to this page, and select "Stream from the MP4 source".
                  <a href="#">Learn more</a>
                </div>
                <hr />
                <div v-if="streamMode === 'h264_copy'">
                  <label for="h264HttpUrlInput">MP4 Source URL:</label>
                  <b-form-input
                    id="h264HttpUrlInput"
                    :placeholder="'MP4 source URL'"
                    v-model="h264HttpUrl"
                  />
                </div>
                <div v-if="streamMode === 'h264_rtsp'">
                  <label for="h264HttpUrlInput">RTSP Port:</label>
                  <b-input
                    v-if="streamMode === 'h264_rtsp'"
                    v-model="rtspPort"
                    :placeholder="'RTSP Port'"
                  />
                </div>
                <small
                  >You only need to change
                  {{ streamMode === 'h264_rtsp' ? 'RTSP Port' : 'MP4 Source URL' }} if you have a
                  custom {{ newCameraStackDisplayName }} installation. If the webcam is working in
                  the preview, don't change it. <a href="#">Learn more</a></small
                >
              </div>
              <hr />
              <b-button
                class="mb-3"
                :disabled="!untestedSettingChanges"
                @click="testCameraButtonPress"
                >Test Streaming Settings</b-button
              >
              <b-button variant="primary" class="mb-3" @click="saveCameraButtonPress"
                >Save</b-button
              >
            </div>
            <div class="content-column">
              <h2>Webcam Preview</h2>
              <div>Use this preview to check if the webcam works correctly.</div>
              <div class="streaming-wrap">
                <div v-if="!webrtc" class="loading-wrap">
                  <loading-placeholder />
                  <small class="creating-stream-text">Creating Stream...</small>
                </div>
                <div v-else>
                  <div v-if="webrtc" class="stream-container">
                    <div ref="streamInner" class="stream-inner">
                      <streaming-box :webcam="webcamTestResult" :webrtc="webrtc">
                        <template #fallback>
                          <div>Your webcam stream is not working.</div>
                          <div>Use the "Troubleshoot Tips" button to figure out the problem.</div>
                        </template>
                      </streaming-box>
                    </div>
                  </div>
                  <div v-if="webcamTestResult?.error" class="text-danger">
                    <h4>The webcam streaming process has run into error(s):</h4>
                    <p>{{ webcamTestResult?.error }}</p>
                  </div>
                  <h3>Webcam stream not working correctly?</h3>
                  <b-button @click="showTroubleshootingTips">Troubleshooting Tips</b-button>
                  <div v-if="troubleshootingDialogOpen">
                    <div>Follow these steps to troubleshoot:</div>
                    <ol>
                      <li>
                        Make sure webcam "{{ selectedWebcam }}" works correctly in
                        {{ agentUIDisplayName }}.
                      </li>
                      <li v-if="streamMode === 'h264_rtsp' && printer.isAgentMoonraker">
                        Make sure you have <a href="#">turned on RTSP in Crowsnest V4</a> and
                        restarted the Raspberry Pi.
                      </li>
                      <li v-if="streamMode === 'h264_rtsp' && !printer.isAgentMoonraker">
                        Make sure you have
                        <a href="#">turned on RTSP in the OctoPrint new camera stack</a> and
                        restarted the Raspberry Pi.
                      </li>
                      <li v-if="streamMode === 'h264_rtsp'">
                        Make sure the RTSP Port "{{ rtspPort }}" is correct. The default value is
                        usually correct unless you have made changes to the default streaming
                        settings in {{ newCameraStackDisplayName }}, or have multiple webcams.
                      </li>
                      <li v-if="streamMode === 'h264_rtsp' && printer.isAgentMoonraker">
                        If the webcam stream tests okay here but goes dark after a few hours, you
                        are one of the unlucky users with the Raspberry Pi 4Bs that don't work well
                        with RTSP. In this case, please come back here and switch to "Stream from
                        the MP4 source".
                      </li>
                      <li v-if="streamMode === 'h264_copy'">
                        Make sure the MP4 source URL "{{ h264HttpUrl }}" is correct. The default
                        value is usually correct unless you have made changes to the default
                        streaming settings in {{ newCameraStackDisplayName }}, or have multiple
                        webcams.
                      </li>
                      <li v-if="streamMode === 'h264_copy'">
                        The WebRTC streaming in {{ newCameraStackDisplayName }} is relatively new
                        and hence still has some outstanding bugs. Some of these bugs will cause the
                        stream to fail in the Obico app even if it works in
                        {{ agentUIDisplayName }}. You can try the legacy MJPEG-Streamer in
                        {{ agentUIDisplayName }}, and come back here to try it again.
                      </li>
                      <li>
                        Follow
                        <a href="#">our comprehensive webcam streaming troubleshooting guide</a>.
                      </li>
                      <li>
                        When everything fails,
                        <a href="https://obico.io/docs/user-guides/contact-us-for-support/"
                          >get help from a human</a
                        >.
                      </li>
                    </ol>
                  </div>
                </div>
                <br />
                <b-button @click="$router.go(-1)">Close Setup page</b-button>
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
import find from 'lodash/find'

import { normalizedPrinter } from '@src/lib/normalizers'
import WebRTCConnection from '@src/lib/webrtc'
import { printerCommManager } from '@src/lib/printer-comm'
import StreamingBox from '@src/components/StreamingBox'
import {
  shutdownWebcamStreamer,
  PassThruTimeOutError,
  fetchAgentWebcams,
  startWebcamStreamer,
} from '@src/lib/printer-passthru'

export default {
  name: 'PrinterCameraSetupPage',

  components: {
    PageLayout,
    StreamingBox,
  },
  data: function () {
    return {
      printer: null,
      webrtc: null,
      webcamTestResult: null,
      webcams: null,
      selectedWebcam: null,
      selectedWebcamData: null,
      streamMode: null,
      h264HttpUrl: null,
      rtspPort: null,
      configuredCameras: [],
      errorMessage: null,
      actionMessage: 'Fetching printer info',
      untestedSettingChanges: false,
      troubleshootingDialogOpen: false,
    }
  },

  computed: {
    isWebRTCCameraStreamer() {
      if (!this.selectedWebcamData) return false
      return this.selectedWebcamData.service === 'webrtc-camerastreamer'
    },

    streamingParams() {
      if (!this.selectedWebcamData) return null

      const params = { mode: this.streamMode }
      if (this.streamMode === 'h264_copy') {
        params.h264_http_url = this.h264HttpUrl
      } else if (this.streamMode === 'h264_rtsp') {
        params.rtsp_port = this.rtspPort
      }

      return params
    },

    agentUIDisplayName() {
      return this.printer.isAgentMoonraker() ? 'Mainsail/Fluidd' : 'OctoPrint'
    },

    newCameraStackDisplayName() {
      return this.printer.isAgentMoonraker() ? 'Crowsnest V4' : 'the OctoPi new camera stack'
    },
  },

  watch: {
    selectedWebcam: 'streamSettingsChanged',
    rtspPort: 'streamSettingsChanged',
    streamMode: 'streamSettingsChanged',
    h264HttpUrl: 'streamSettingsChanged',
  },

  async created() {
    const printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    await this.fetchPrinter(printerId)

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
      this.actionMessage = 'Fetching printer info...'
      const printerApiCall = axios.get(urls.printer(printerId))
      const cameraApiCall = axios.get(urls.cameras(printerId))

      Promise.all([printerApiCall, cameraApiCall])
        .then(([printerApiResp, cameraApiResp]) => {
          this.printer = normalizedPrinter(printerApiResp.data)
          this.configuredCameras = cameraApiResp.data
        })
        .catch(() => {
          this.errorMessage = 'Failed to connect to Obico server'
        })
        .finally(() => {
          this.actionMessage = null
        })
    },

    streamSettingsChanged() {
      this.untestedSettingChanges = true
    },

    webcamSelectionChanged() {
      if (!this.selectedWebcam) {
        return
      }

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

      this.testWebcamStream()
    },

    testWebcamStream() {
      this.actionMessage = `Starting webcam stream for ${this.selectedWebcam}`

      if (this.webrtc) {
        this.webrtc.disconnect()
        this.webrtc = null
      }
      startWebcamStreamer(this.printerComm, this.selectedWebcam, this.streamingParams)
        .then((ret) => {
          const streamId = ret?.[0]?.stream_id
          const streamMode = ret?.[0]?.stream_mode
          if (streamId === undefined || streamMode === undefined) {
            throw 'Webcam start failed to start for unknown reason. You can trouble-shoot the problem by following this guide.'
          } else {
            this.webcamTestResult = ret[0]
            this.webrtc = WebRTCConnection(streamMode, streamId)
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
          }
        }, 60)
        .catch((err) => {
          this.errorMessage = err
        })
        .finally(() => {
          this.actionMessage = null
          this.untestedSettingChanges = false
        })
    },

    shutdownStreamButtonPressed() {
      this.actionMessage = 'Shutting down Obico webcam stream(s)...'
      shutdownWebcamStreamer(this.printerComm)
        .then(() => {
          this.actionMessage = `Retrieving webcam configuration in ${this.agentUIDisplayName}...`
          return fetchAgentWebcams(this.printerComm, this.printer)
        })
        .then((ret) => {
          this.webcams = ret?.webcams
        })
        .catch((err) => {
          this.handlePassThruError(err)
        })
        .finally(() => {
          this.actionMessage = null
        })
    },

    testCameraButtonPress() {
      this.testWebcamStream()
    },

    async saveCameraButtonPress() {
      let confirmPrompt
      if (this.untestedSettingChanges) {
        confirmPrompt = this.$swal.Prompt.fire({
          title: 'Are you sure?',
          html: `
          <p style="text-align:center">You haven't tested current webcam configuration. Please test it to verify your webcam works first.</p>
          `,
          showCancelButton: true,
          confirmButtonText: 'Okay',
          cancelButtonText: 'Save it Anyway!!!',
        })
      } else {
        confirmPrompt = this.$swal.Prompt.fire({
          title: 'Are you sure?',
          html: `
          <p style="text-align:center">Please verify stream is working as expected. <br/> For more information please visit <a target="_blank" href="https://www.obico.io/docs/user-guides/webcam-feed-is-not-showing/">our help docs</a>.</p>
          `,
          showCancelButton: true,
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
        })
      }
      confirmPrompt.then(async (userAction) => {
        // When untestedSettingChanges, we switch the confirm and cancel buttons
        const willSave = this.untestedSettingChanges
          ? !userAction.isConfirmed
          : userAction.isConfirmed
        if (willSave) {
          this.saveWebcamConfig()
        }
      })
    },

    async saveWebcamConfig() {
      const camera_config = {
        printer_id: this.printer.id,
        name: this.selectedWebcam,
        streaming_params: this.streamingParams,
      }
      const configuredCamera = find(this.configuredCameras, { name: this.selectedWebcam })
      if (configuredCamera) {
        await axios.patch(urls.camera(configuredCamera.id), camera_config)
      } else {
        await axios.post(urls.cameras(), camera_config)
      }
    },

    deleteWebcamConfiguration(webcam) {
      axios.delete(urls.camera(webcam.id)).then(() => {
        this.getConfiguredWebcams()
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

    handlePassThruError(err) {
      if (err instanceof PassThruTimeOutError) {
        this.errorMessage = `Failed to connect to your printer. Please make sure your printer is powered up and Obico
          for ${this.printer.agentDisplayName()} is linked and running correctly.`
      } else {
        this.errorMessage = err
      }
    },
    showTroubleshootingTips() {
      this.troubleshootingDialogOpen = true
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
