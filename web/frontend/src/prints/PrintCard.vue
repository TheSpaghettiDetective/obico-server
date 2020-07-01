<template>
  <div class="col-sm-12 col-md-6 col-lg-4 pt-3">
    <div class="card vld-parent">
      <loading :active="videoDownloading" :is-full-page="true"></loading>
      <div class="card-header">
        <div :style="{visibility: hasSelectedChangedListener ? 'visible' : 'hidden'}">
          <b-form-checkbox
            v-model="selected"
            @change="onSelectedChange"
            size="lg"
            class="text-decoration-none"
          ></b-form-checkbox>
        </div>
        <b-form-radio-group
          v-model="selectedCardView"
          buttons
          button-variant="outline-primary"
          name="radio-btn-outline"
        >
          <b-form-radio
            value="detective"
            class="no-corner no-shadow"
            :disabled="!canShowDetectiveView"
          >
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/logo-square-inverted.png')"
            />
          </b-form-radio>
          <b-form-radio value="info" class="no-corner no-shadow">
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/info-inverted.png')"
            />
          </b-form-radio>
        </b-form-radio-group>

        <div class="dropdown">
          <button
            class="btn icon-btn"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-label="Controls"
          >
            <i class="fas fa-ellipsis-v"></i>
          </button>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
            <a class="dropdown-item" v-if="this.print.video_url" @click="downloadVideo(false)">
              <i class="fas fa-download"></i>Download Original Time-lapse
            </a>
            <a
              class="dropdown-item"
              v-if="this.print.tagged_video_url"
              @click="downloadVideo(true)"
            >
              <i class="fas fa-download"></i>Download Detective Time-lapse
            </a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item text-danger" @click="deleteVideo">
              <i class="fas fa-trash-alt"></i>Delete
            </a>
          </div>
        </div>
      </div>
      <div>
        <video-box
          v-if="videoUrl"
          :videoUrl="videoUrl"
          :posterUrl="print.poster_url"
          :fluid="true"
          :fullscreenBtn="hasFullscreenListener"
          @timeupdate="onTimeUpdate"
          @fullscreen="$emit('fullscreen', print.id, videoUrl)"
        />
        <div v-else>
          <detective-working />
        </div>
        <div v-show="cardView == 'info'">
          <div class="card-body">
            <div class="container">
              <div class="row">
                <div class="text-muted col-4">
                  File
                  <span class="float-right">:</span>
                </div>
                <div class="col-8">{{ print.filename }}</div>
              </div>
              <div class="row">
                <div class="text-muted col-4">
                  {{ wasTimelapseUploaded ? "Uploaded" : "Printed" }}
                  <span class="float-right">:</span>
                </div>
                <div
                  class="col-8"
                >{{ wasTimelapseUploaded ? print.uploaded_at.fromNow() : print.ended_at.fromNow() }} {{ endStatus }}</div>
              </div>
              <div class="row" v-if="!wasTimelapseUploaded">
                <div class="text-muted col-4">
                  Duration
                  <span class="float-right">:</span>
                </div>
                <div class="col-8">{{ duration.humanize() }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="cardView == 'detective'">
          <gauge
            v-if="print.prediction_json_url"
            :predictionJsonUrl="print.prediction_json_url"
            :currentPosition="currentPosition"
          />
          <div class="feedback-section">
            <div class="text-center py-2 px-3">
              <div
                class="lead"
                :class="[print.alerted_at ? 'text-danger' : 'text-success', ]"
              >{{ print.alerted_at ? 'The Detective found spaghetti' : 'The Detective found nothing fishy' }}</div>
              <div class="py-2">
                Did she get it right?
                <b-button
                  :variant="thumbedUp ? 'primary' : 'outline'"
                  @click="onThumbUpClick"
                  class="mx-2 btn-sm"
                >
                  <b-spinner v-if="inflightAlertOverwrite" type="grow" small></b-spinner>
                  <i v-else class="fas fa-thumbs-up"></i>
                </b-button>
                <b-button
                  :variant="thumbedDown ? 'primary' : 'outline'"
                  @click="onThumbDownClick"
                  class="mx-2 btn-sm"
                >
                  <b-spinner v-if="inflightAlertOverwrite" type="grow" small></b-spinner>
                  <i v-else class="fas fa-thumbs-down"></i>
                </b-button>
              </div>
              <transition name="bounce">
                <div v-if="focusedFeedbackEligible" class="pt-2">
                  <a
                    role="button"
                    class="btn btn-sm btn-outline-primary px-4"
                    :href="focusedFeedbackLink"
                  >
                    F
                    <i class="fas fa-search focused-feedback-icon"></i>CUSED FEEDBACK
                    <img
                      v-if="!focusedFeedbackCompleted"
                      class="seg-control-icon ml-1"
                      :src="require('../../../app/static/img/detective-hour-2-primary.png')"
                    />
                  </a>
                </div>
              </transition>
            </div>
            <div class="text-muted py-2 px-3 help-text">
              <small v-if="focusedFeedbackEligible">
                <span
                  v-if="focusedFeedbackCompleted"
                >Thank you for completing the Focused Feedback for The Detective. You have earned 2 non-expirable Detective Hours. You can click the botton again to change your feedback.</span>
                <span v-else>
                  With Focused Feedback, you can tell The Detective exactly where she got it wrong. This is the most effective way to help her improve.
                  <a
                    href="https://www.thespaghettidetective.com/docs/how-does-credits-work/#you-earn-detective-hours-for-giving-focused-feedback"
                  >You will earn 2 Detective Hours once you finish the Focused Feedback</a>.
                </span>
              </small>

              <small v-else>
                Every time you give The Detective feedback,
                <a
                  href="https://www.thespaghettidetective.com/docs/help-the-detective-improve/"
                >you help her get better at detecting spaghetti</a>.
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import fileDownload from 'js-file-download'
import moment from 'moment'
import filter from 'lodash/filter'
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'

import apis from '../lib/apis'
import VideoBox from '../common/VideoBox'
import Gauge from '../common/Gauge'
import DetectiveWorking from 'common/DetectiveWorking'

export default {
  name: 'PrintCard',

  components: {
    Loading,
    VideoBox,
    Gauge,
    DetectiveWorking
  },

  data: () => {
    return {
      videoDownloading: false,
      currentPosition: 0,
      selectedCardView: 'detective',
      selected: false,
      inflightAlertOverwrite: null
    }
  },

  props: {
    print: Object
  },

  computed: {
    wasTimelapseUploaded() {
      return this.print.uploaded_at !== null
    },

    endStatus() {
      return this.print.cancelled_at ? '(Cancelled)' : ''
    },

    duration() {
      return moment.duration(this.print.ended_at.diff(this.print.started_at))
    },

    canShowDetectiveView() {
      if (
        this.print.prediction_json_url !== null &&
        this.print.tagged_video_url !== null
      ) {
        return true
      }
      // Time-lapses that finished or was uploaded within the past 24 hours are presumably still be processed
      if (
        (this.print.ended_at &&
          moment().diff(this.print.ended_at, 'hours') < 24) ||
        (this.print.uploaded_at &&
          moment().diff(this.print.uploaded_at, 'hours') < 24)
      ) {
        return true
      }
      return false
    },

    cardView() {
      return this.canShowDetectiveView ? this.selectedCardView : 'info'
    },

    videoUrl() {
      return this.cardView == 'info'
        ? this.print.video_url
        : this.print.tagged_video_url
    },

    thumbedUp() {
      if (!this.print.alert_overwrite) {
        return false
      }
      return (
        this.print.has_alerts ^ (this.print.alert_overwrite === 'NOT_FAILED')
      )
    },

    thumbedDown() {
      if (!this.print.alert_overwrite) {
        return false
      }
      return this.print.has_alerts ^ (this.print.alert_overwrite === 'FAILED')
    },

    focusedFeedbackEligible() {
      return (
        this.print.printshotfeedback_set.length > 0 &&
        this.print.alert_overwrite
      )
    },

    focusedFeedbackCompleted() {
      return (
        this.print.printshotfeedback_set.length > 0 &&
        filter(this.print.printshotfeedback_set, f => !f.answered_at).length ==
          0
      )
    },

    focusedFeedbackLink() {
      return `/prints/shot-feedback/${this.print.id}/`
    },

    hasSelectedChangedListener() {
      return Boolean(this.$listeners && this.$listeners.selectedChanged)
    },

    hasFullscreenListener() {
      return Boolean(this.$listeners && this.$listeners.fullscreen)
    }
  },

  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition
    },

    onSelectedChange() {
      this.$emit('selectedChanged', this.print.id, !this.selected) // this method is called before this.selected is flipped. So need to inverse it before passing it event listener
    },

    downloadVideo(detectiveVideo) {
      this.videoDownloading = true
      const x = new XMLHttpRequest()
      const filename = `${this.print.filename}${
        detectiveVideo ? '_detective_view' : ''
      }.mp4`
      x.open(
        'GET',
        detectiveVideo ? this.print.tagged_video_url : this.print.video_url,
        true
      )
      x.responseType = 'blob'
      x.onload = e => {
        fileDownload(e.target.response, filename)
        this.videoDownloading = false
      }
      x.send()
    },

    deleteVideo() {
      axios.delete(apis.print(this.print.id)).then(() => {
        this.$emit('printDeleted', this.print.id)
      })
    },

    onThumbUpClick() {
      this.inflightAlertOverwrite = this.print.has_alerts
        ? 'FAILED'
        : 'NOT_FAILED'
      this.alertOverwrite(this.inflightAlertOverwrite)
    },

    onThumbDownClick() {
      this.inflightAlertOverwrite = this.print.has_alerts
        ? 'NOT_FAILED'
        : 'FAILED'
      this.alertOverwrite(this.inflightAlertOverwrite)
    },

    alertOverwrite(value) {
      axios
        .post(apis.printAlertOverwrite(this.print.id), { value })
        .then(response => {
          this.$emit('printDataChanged', response.data)
          this.inflightAlertOverwrite = null
        })
    }
  },
  mounted() {
    if (!this.print.tagged_video_url) {
      this.selectedCardView = 'info'
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.card-header
  display: flex
  flex-flow: row nowrap
  justify-content: space-between
  align-items: center

.seg-control-icon
  height: 1.2rem

.feedback-section
  background-color: theme.$color-bg-dark

.bounce-enter-active
  animation: bounce-in .5s

.bounce-leave-active
  animation: bounce-in .5s reverse

@keyframes bounce-in
  0%
    transform: scale(0)
  50%
    transform: scale(1.5)
  100%
    transform: scale(1)

.help-text
  line-height: 1.2
</style>
