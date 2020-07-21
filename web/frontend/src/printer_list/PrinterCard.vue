<template>
  <div :id="printer.id"
    class="col-sm-12 col-lg-6 printer-card"
  >
    <div class="card">
      <div class="card-header">
        <div class="title-box">
          <div class="primary-title print-filename"></div>
          <div class="printer-name">{{ printer.name || 'Printer #' + printer.id }}</div>
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
        <div
          :class="rotate_class"
        >
          <div
            class="webcam_fixed_ratio"
            :class="webcam_ratio_class"
          >
            <div class="webcam_fixed_ratio_inner full">
              <img
                class="tagged-jpg"
                :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
                :src="require('@static/img/3d_printer.png')"
                :alt="printer.name + ' current image'"
            />
            </div>
            <div id="webrtc-stream" class="webcam_fixed_ratio_inner full ontop">
              <video
                class="remote-video hide"
                :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
                width=960
                :height="webcam_video_height"
                autoplay muted playsinline>
              </video>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="failureDetected"
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

      <div class="card-body gauge-container">
        <div class="overlay-top text-center"
          style="left: 50%; margin-left: -102px; top: 50%; margin-top: -15px;">
          <div>The Detective Is Not Watching</div>
          <div>(<a href="https://www.thespaghettidetective.com/docs/detective-not-watching/">Why?</a>)</div>
        </div>
        <gauge
          :predictionJsonUrl="printer.prediction_json_url"
          :currentPosition="0"
        />
        <hr />
      </div>
      <div id="printer-actions" class="container">
      </div>
      <div class="info-section settings">
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.settings}"
          @click="section_toggles.settings = !section_toggles.settings"
        ><i class="fas fa-cog fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.time}"
          @click="section_toggles.time = !section_toggles.time"
        ><i class="fas fa-clock fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.status_temp}"
          @click="section_toggles.status_temp = !section_toggles.status_temp"
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
                  <label class="toggle-label" :for="'watching-toggle-' + printer.id">Watch for failures
                    <div class="text-muted font-weight-light font-size-sm">Subsequent prints NOT watched until turned
                      on.</div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input type="checkbox" name="watching" class="custom-control-input update-printer"
                      :id="'watching-toggle-' + printer.id">
                    <label class="custom-control-label" for="'watching-toggle-' + printer.id"
                      style="font-size: 1rem;"></label>
                  </div>
                </div>
              </div>
              <div class="row justify-content-center px-3">
                <div class="col-12 setting-item">
                  <label class="toggle-label" for="'pause-toggle-' + printer.id">Pause on detected failures<div
                      class="text-muted font-weight-light font-size-sm">You will still be alerted via notifications
                    </div></label>
                  <div class="custom-control custom-switch">
                    <input type="checkbox" name="pause_on_failure" class="custom-control-input update-printer"
                      id="pause-toggle-printer.id">
                    <label class="custom-control-label" for="pause-toggle-printer.id"
                      style="font-size: 1rem;"></label>
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
                <div id="print-time-remaining" class="col-5 numbers">{{ time_remaining }}</div>
                <div id="print-time-total" class="col-5 numbers">{{ time_total }}</div>
                <div class="col-12">
                  <div class="progress" style="height: 2px;">
                    <div id="print-progress" class="progress-bar progress-bar-striped progress-bar-animated"
                      role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div
            id="status_temp_block"
            v-if="section_toggles.status_temp"
          >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Gauge from '@common/Gauge'

export default {
  name: 'PrinterCard',
  components: {
    Gauge,
  },
  props: {
    printer: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      section_toggles: {
        settings: true,
        time: true,
        status_temp: true
      }
    }
  },
  computed: {
    failureDetected() {
      return true // FIXME
    },
    time_remaining() {
      return '-' // FIXME
    },
    time_total() {
      return '-' // FIXME
    },
    webcam_rotate_class() {
      switch (this.printer.settings.webcam_rotate90) {
      case true:
        return 'webcam_rotated'
      case false:
        return 'webcam_unrotated'
      default:
        return 'webcam_unrotated'
      }
    },
    webcam_ratio_class() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 'ratio169'
      case false:
        return 'ratio43'
      default:
        return 'ratio43'
      }
    },
    webcam_video_height() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 540
      case false:
        return 720
      default:
        return 720
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
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

</style>
