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
        <div class="dropdown">
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

            <div class="dropdown-divider"></div>

            <a
              class="dropdown-item"
              :href="settingsUrl()"
            ><i class="fas fa-cog fa-lg"></i>Settings
            </a>

            <a
              id="delete-print"
              class="dropdown-item text-danger"
              href="#"
              @click="$emit('DeleteClicked', printer.id)"
            ><i class="fas fa-trash-alt fa-lg"></i>Delete
            </a>
          </div>
        </div>
      </div>

      <!-- webcam stream include TODO -->
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
        v-if="printer.alertUnacknowledged"
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
        class="card-body gauge-container"
        :class="{overlay: !isWatching}"
      >
        <div
          v-if="!isWatching"
          class="overlay-top text-center"
          style="left: 50%; margin-left: -102px; top: 50%; margin-top: -15px;"
        >
          <div>The Detective Is Not Watching</div>
          <div>(<a href="https://www.thespaghettidetective.com/docs/detective-not-watching/">Why?</a>)</div>
        </div>
        <DirectGauge
          :ewm_mean="ewm_mean"
        />
        <hr />
      </div>
      <PrinterActions
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
      <div class="info-section settings">
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
      <div>
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
                    :for="'watching-toggle-' + printer.id"
                  >Watch for failures
                    <div
                      v-if="!watchForFailures"
                      class="text-muted font-weight-light font-size-sm">Subsequent prints NOT watched until turned on.
                    </div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input
                      type="checkbox"
                      name="watching"
                      class="custom-control-input update-printer"
                      :id="'watching-toggle-' + printer.id"
                      @click="$emit('WatchForFailuresToggled')"
                      :checked="watchForFailures"
                    >
                    <label
                      class="custom-control-label"
                      :for="'watching-toggle-' + printer.id"
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
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'
import capitalize from 'lodash/capitalize'
import DirectGauge from '@common/DirectGauge'

import printerStockImgSrc from '@static/img/3d_printer.png'
import loadingIconSrc from '@static/img/loading.gif'

import {
  setPrinterLocalPref,
  getPrinterLocalPref,
  toDuration,
} from '@lib/printers.js'

import DurationBlock from './DurationBlock.vue'
import PrinterActions from './PrinterActions.vue'
import StatusTemp from './StatusTemp.vue'

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
    DirectGauge,
    DurationBlock,
    PrinterActions,
    StatusTemp,
  },
  props: {
    printer: {
      type: Object,
      required: true
    },
    isOnSharedPage: { // TODO
      type: Boolean,
      required: true
    },
    isVideoVisible: {
      type: Boolean,
      required: true
    },
  },
  data() {
    return {
      poster: loadingIconSrc,
      section_toggles: {
        settings: getPrinterLocalPref(
          LocalPrefNames.Settings,
          this.printer.id,
          Show
        ),
        time: getPrinterLocalPref(
          LocalPrefNames.Time,
          this.printer.id,
          Hide,
        ),
        statusTemp: getPrinterLocalPref(
          LocalPrefNames.StatusTemp,
          this.printer.id,
          Show
        ),
      },
      stickyStreamingSrc: null,
    }
  },
  computed: {
    ewm_mean() {
      return get(this.printer, 'printerprediction.ewm_mean', 0)
    },
    isWatching() {
      return this.printer.should_watch && get(this.printer, 'status.state.flags.printing')
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
      return this.printer.watching
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
    forceStreamingSrc(src) {
      this.stickyStreamingSrc = src
    },
    onSettingsToggleClicked() {
      this.section_toggles.settings = !this.section_toggles.settings
      setPrinterLocalPref(
        LocalPrefNames.Settings,
        this.printer.id,
        this.section_toggles.settings)
    },
    onTimeToggleClicked() {
      this.section_toggles.time = !this.section_toggles.time
      setPrinterLocalPref(
        LocalPrefNames.Time,
        this.printer.id,
        this.section_toggles.time)
    },
    onStatusTempToggleClicked() {
      this.section_toggles.statusTemp = !this.section_toggles.statusTemp
      setPrinterLocalPref(
        LocalPrefNames.StatusTemp,
        this.printer.id,
        this.section_toggles.statusTemp)
    },
    onCanPlay() {
      this.poster = ''
    },
    onLoadStart() {
      this.poster = loadingIconSrc
    },
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

</style>
