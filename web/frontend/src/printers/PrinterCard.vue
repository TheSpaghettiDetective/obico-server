<template>
  <div :id="printer.id"
    class="col-sm-12 col-lg-6 printer-card"
  >
    <div class="card">
      <div class="card-header">
        <div class="title-box">
          <div
            v-if="hasCurrentPrintFilename"
            class="primary-title print-filename"
          >{{ printer.current_print.filename }}</div>
          <div
            class="printer-name"
            :class="{'secondary-title': hasCurrentPrintFilename}"
          >{{ printer.name }}</div>
        </div>
        <div v-if="!shareToken" class="dropdown">
          <button
            class="btn icon-btn"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            :aria-label="printer.name + ' Controls'"
          ><i class="fas fa-ellipsis-v"></i>
          </button>

          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">

            <a class="dropdown-item" :href="shareUrl()">
              <i class="fas fa-share-alt fa-lg"></i>Share
            </a>
            <a class="dropdown-item" :href="octoPrintTunnelUrl()">
              <img class="menu-icon" :src="require('@static/img/octoprint-tunnel.png')" />
              Tunneling
            </a>

            <div class="dropdown-divider"></div>

            <a
              class="dropdown-item"
              :href="settingsUrl()"
            ><i class="fas fa-cog fa-lg"></i>Settings
            </a>
          </div>
        </div>
      </div>

      <div class="card-img-top webcam_container">
        <div v-if="isVideoVisible && taggedImgAvailable" class="streaming-switch">
          <button type="button" class="btn btn-sm no-corner" :class="{ active: showVideo }" @click="forceStreamingSrc('VIDEO')"><i class="fas fa-video"></i></button>
          <button type="button" class="btn btn-sm no-corner " :class="{ active: !showVideo }" @click="forceStreamingSrc('IMAGE')"><i class="fas fa-camera"></i></button>
        </div>
        <div
          :class="webcamRotateClass"
        >
          <div
            class="webcam_fixed_ratio"
            :class="webcamRatioClass"
          >
            <div
              class="webcam_fixed_ratio_inner full"
            >
              <img
                class="tagged-jpg"
                :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
                :src="taggedSrc"
                :alt="printer.name + ' current image'"
              />
            </div>
            <div
              v-show="showVideo"
              id="webrtc-stream"
              class="webcam_fixed_ratio_inner ontop full"
            >
              <video
                ref="video"
                class="remote-video"
                :class="{hide: !isVideoVisible, flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
                width=960
                :height="webcamVideoHeight"
                :poster="poster"
                autoplay muted playsinline
                @loadstart="onLoadStart()"
                @canplay="onCanPlay()"
              ></video>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="printer.alertUnacknowledged && !shareToken"
        class="failure-alert card-body bg-warning px-2 py-1"
      >
        <i class="fas fa-exclamation-triangle align-middle"></i>
        <span class="align-middle">Failure Detected!</span>
        <button
          type="button"
          id="not-a-failure"
          class="btn btn-outline-primary btn-sm float-right"
          @click="$emit('NotAFailureClicked', printer.id)"
        >Not a failure?</button>
      </div>

      <div
        v-if="!shareToken"
        class="card-body gauge-container"
        :class="{overlay: !isWatching}"
      >
        <div
          v-if="!isWatching"
          class="overlay-top text-center"
          style="left: 50%; margin-left: -102px; top: 50%; margin-top: -15px;"
        >
          <div class="text-warning">The Detective Is Not Watching</div>
          <small
            v-if="printer.not_watching_reason"
          >{{ printer.not_watching_reason }}. <a href="https://www.thespaghettidetective.com/docs/detective-not-watching/" target="_blank">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a></small>
          <div></div>
        </div>
        <Gauge
          :normalized_p="printer.normalized_p"
        />
        <hr />
      </div>
      <PrinterActions
        v-if="!shareToken"
        id="printer-actions"
        class="container"
        v-bind="actionsProps"
        @PrinterActionPauseClicked="$emit('PrinterActionPauseClicked', $event)"
        @PrinterActionResumeClicked="$emit('PrinterActionResumeClicked', $event)"
        @PrinterActionCancelClicked="$emit('PrinterActionCancelClicked', $event)"
        @PrinterActionConnectClicked="$emit('PrinterActionConnectClicked', $event)"
        @PrinterActionStartClicked="$emit('PrinterActionStartClicked', $event)"
        @PrinterActionControlClicked="$emit('PrinterActionControlClicked', $event)"
      ></PrinterActions>
      <div v-if="!shareToken" class="info-section settings">
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.settings}"
          @click="onSettingsToggleClicked()"
        ><i class="fas fa-cog fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.time}"
          @click="onTimeToggleClicked()"
        ><i class="fas fa-clock fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.statusTemp}"
          @click="onStatusTempToggleClicked()"
          ><i class="fas fa-thermometer-half fa-lg"></i></button>
      </div>
      <div class="info-section" style="height: 0.3rem;"></div>
      <div v-if="!shareToken">
        <div class="info-section container">
          <div
            id="panel-settings"
            v-if="section_toggles.settings"
          >
            <div class="pt-2 pb-3">
              <div class="row justify-content-center px-3">
                <div class="col-12 setting-item">
                  <label
                    class="toggle-label"
                    :for="'watching_enabled-toggle-' + printer.id"
                  >Watch for failures
                    <div
                      v-if="!watchForFailures"
                      class="text-muted font-weight-light font-size-sm">Subsequent prints NOT watched until turned on.
                    </div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input
                      type="checkbox"
                      name="watching_enabled"
                      class="custom-control-input update-printer"
                      :id="'watching_enabled-toggle-' + printer.id"
                      @click="$emit('WatchForFailuresToggled')"
                      :checked="watchForFailures"
                    >
                    <label
                      class="custom-control-label"
                      :for="'watching_enabled-toggle-' + printer.id"
                      style="font-size: 1rem;"
                    ></label>
                  </div>
                </div>
              </div>
              <div class="row justify-content-center px-3">
                <div class="col-12 setting-item">
                  <label
                    class="toggle-label"
                    :for="'pause-toggle-' + printer.id"
                  >Pause on detected failures
                    <div
                      v-if="!pauseOnFailure"
                      class="text-muted font-weight-light font-size-sm">You will still be alerted via notifications
                    </div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input
                      type="checkbox"
                      name="pause_on_failure"
                      class="custom-control-input update-printer"
                      :id="'pause-toggle-' + printer.id"
                      @click="$emit('PauseOnFailureToggled')"
                      :checked="pauseOnFailure"
                    >
                    <label
                      class="custom-control-label"
                      :for="'pause-toggle-'+printer.id"
                      style="font-size: 1rem;">
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div
            v-if="section_toggles.time"
            id="print-time">
            <div class="py-2">
              <div class="row text-muted">
                <small class="col-5 offset-2">
                  Remaining
                </small>
                <small class="col-5">
                  Total
                </small>
              </div>
              <div class="row">
                <div class="col-2 text-muted">
                  <i class="fas fa-clock"></i>
                </div>
                <duration-block
                  id="print-time-remaining"
                  class="col-5 numbers"
                  v-bind="timeRemaining"
                ></duration-block>
                <duration-block
                  id="print-time-total"
                  class="col-5 numbers"
                  v-bind="timeTotal"
                ></duration-block>
                <div class="col-12">
                  <div class="progress" style="height: 2px;">
                    <div
                      id="print-progress"
                      class="progress-bar"
                      :class="{'progress-bar-striped': progressPct < 100, 'progress-bar-animated': progressPct < 100}"
                      role="progressbar"
                      aria-valuenow="0"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :style="`width: ${progressPct}%;`">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <StatusTemp
            v-if="section_toggles.statusTemp && statusTempProps.show"
            id="status_temp_block"
            v-bind="statusTempProps"
            @TempEditClicked="$emit('TempEditClicked', $event)"
          ></StatusTemp>
        </div>
      </div>
      <div v-if="shareToken" class="p-3 p-md-5">
        <p class="text-center">You are viewing an awesome 3D print your friend shared specifically with you on <a
            href="https://www.thespaghettidetective.com/">The Spaghetti Detective</a></p>
        <p class="text-center"><a href="/accounts/signup/">Sign up an account for FREE >>></a></p>
      </div>
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'
import capitalize from 'lodash/capitalize'
import ifvisible from 'ifvisible'

import Janus from '@lib/janus'
import webrtc from '@lib/webrtc_streaming'
import Gauge from '@common/Gauge'
import printerStockImgSrc from '@static/img/3d_printer.png'
import loadingIconSrc from '@static/img/loading.gif'

import { toDuration } from '@lib/printers.js'
import { getLocalPref, setLocalPref } from '@lib/pref'
import DurationBlock from './DurationBlock.vue'
import PrinterActions from './PrinterActions.vue'
import StatusTemp from './StatusTemp.vue'


let printerWebRTCUrl = printerId => `/ws/janus/${printerId}/`
let printerSharedWebRTCUrl = token => `/ws/share_token/janus/${token}/`

const Show = true
const Hide = false

const LocalPrefNames = {
  Settings: 'panel-settings',
  Time: 'print-time',
  StatusTemp: 'status_temp_block',
}

export default {
  name: 'PrinterCard',
  components: {
    Gauge,
    DurationBlock,
    PrinterActions,
    StatusTemp,
  },
  created() {
        this.webrtc = null
  },
  props: {
    printer: {
      type: Object,
      required: true
    },
    shareToken: {
      type: String,
      required: false
    },
    isProAccount: {
      type: Boolean,
      required: true
    },
  },
  data() {
    return {
      poster: loadingIconSrc,
      section_toggles: {
        settings: getLocalPref(LocalPrefNames.Settings + String(this.printer.id), Show),
        time: getLocalPref(LocalPrefNames.Time + String(this.printer.id), Hide),
        statusTemp: getLocalPref(LocalPrefNames.StatusTemp + String(this.printer.id), Show),
      },
      stickyStreamingSrc: null,
      isVideoVisible: false,
    }
  },
  computed: {
    isWatching() {
      return !this.printer.not_watching_reason
    },
    timeRemaining() {
      return toDuration(
        this.secondsLeft, this.printer.isPrinting)
    },
    timeTotal() {
      let secs = null
      if (this.secondsPrinted && this.secondsLeft) {
        secs = this.secondsPrinted + this.secondsLeft
      }
      return toDuration(
        secs,
        this.printer.isPrinting)
    },
    secondsLeft() {
      return get(this.printer, 'status.progress.printTimeLeft')
    },
    secondsPrinted() {
      return get(this.printer, 'status.progress.printTime')
    },
    taggedImgAvailable() {
      return this.taggedSrc !== printerStockImgSrc
    },
    showVideo() {
      return this.isVideoVisible && this.stickyStreamingSrc !== 'IMAGE'
    },
    webcamRotateClass() {
      switch (this.printer.settings.webcam_rotate90) {
      case true:
        return 'webcam_rotated'
      case false:
        return 'webcam_unrotated'
      default:
        return 'webcam_unrotated'
      }
    },
    webcamRatioClass() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 'ratio169'
      case false:
        return 'ratio43'
      default:
        return 'ratio43'
      }
    },
    webcamVideoHeight() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 540
      case false:
        return 720
      default:
        return 720
      }
    },
    watchForFailures() {
      return this.printer.watching_enabled
    },
    pauseOnFailure() {
      return this.printer.action_on_failure == 'PAUSE'
    },
    hasCurrentPrintFilename() {
      if (this.printer.current_print && this.printer.current_print.filename) {
        return true
      }
      return false
    },
    taggedSrc() {
      return get(this.printer, 'pic.img_url', printerStockImgSrc)
    },
    actionsProps() {
      return {
        printer: this.printer,
      }
    },
    progressPct() {
      return get(this.printer, 'status.progress.completion')
    },
    statusTempProps() {
      // If temp_profiles is missing, it's a plugin version too old to change temps
      let editable = get(this.printer, 'settings.temp_profiles') != undefined
      let temperatures = []
      const keys = ['bed', 'tool0', 'tool1']
      keys.forEach((tempKey) => {
        let temp = get(this.printer, 'status.temperatures.' + tempKey)
        if (temp) {
          temp.actual = parseFloat(temp.actual).toFixed(1)
          temp.target = Math.round(temp.target)
          Object.assign(temp, {toolName: capitalize(tempKey)})
          temp.id = this.printer.id + '-' + tempKey
          temp.key = tempKey
          temperatures.push(temp)
        }
      })
      return {
        temperatures: temperatures,
        show: temperatures.length > 0,
        editable: editable,
      }
    },
  },
  methods: {
    shareUrl() {
      return `/printers/${this.printer.id}/share/`
    },
    settingsUrl() {
      return `/printers/${this.printer.id}/`
    },
    octoPrintTunnelUrl() {
      return `/tunnel/${this.printer.id}/`
    },
    forceStreamingSrc(src) {
      this.stickyStreamingSrc = src
    },
    onSettingsToggleClicked() {
      this.section_toggles.settings = !this.section_toggles.settings
      setLocalPref(LocalPrefNames.Settings + String(this.printer.id), this.section_toggles.settings)
    },
    onTimeToggleClicked() {
      this.section_toggles.time = !this.section_toggles.time
      setLocalPref(LocalPrefNames.Time + String(this.printer.id), this.section_toggles.time)
    },
    onStatusTempToggleClicked() {
      this.section_toggles.statusTemp = !this.section_toggles.statusTemp
      setLocalPref(LocalPrefNames.StatusTemp + String(this.printer.id), this.section_toggles.statusTemp)
    },
    onCanPlay() {
      this.poster = ''
    },
    onLoadStart() {
      this.poster = loadingIconSrc
    },

    openWebRTCForPrinter() {
      let url, token
      if (this.shareToken) {
        url = printerSharedWebRTCUrl(this.shareToken)
        token = this.shareToken
      } else {
        url = printerWebRTCUrl(this.printer.id)
        token = this.printer.auth_token
      }
      this.webrtc.connect(
        url,
        token
      )
    },

    onJanusInitalized() {
      if (!Janus.isWebrtcSupported()) {
        return
      }

      this.webrtc = webrtc.getWebRTCManager({
        onRemoteStream: this.onWebRTCRemoteStream,
        onCleanup: this.onWebRTCCleanup,
      })

      this.openWebRTCForPrinter()
    },

    onWebRTCRemoteStream(stream) {
      Janus.debug(' ::: Got a remote stream :::')
      Janus.debug(stream)
      Janus.attachMediaStream(this.$refs.video, stream)

      var videoTracks = stream.getVideoTracks()
      if (videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
        // No remote video
        this.isVideoVisible = false
      } else {
        this.isVideoVisible = true
      }
    },

    onWebRTCCleanup() {
      this.isVideoVisible = false
    },
  },
  mounted() {
    if (this.isProAccount) {
      Janus.init({
        debug: 'all',
        callback: this.onJanusInitalized
      })
    }

    ifvisible.on('blur', () => {
      if (this.webrtc) {
        this.webrtc.stopStream()
      }
    })

    ifvisible.on('focus', () => {
      if (this.webrtc) {
        this.webrtc.startStream()
      }
    })
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.streaming-switch
  background-color: rgba(255, 255, 255, 0.4)
  border: solid thin #888
  position: absolute
  display: flex
  flex-flow: column
  right: 4px
  top: 4px
  z-index: 100

  .btn
    color: #444444
    &.active
      color: #ffffff
      background-color: rgba(0,0,0,0.6)

.menu-icon
  width: 20px
  margin-right: 12px

</style>
