<template>
  <layout>
    <template v-slot:content>
      <b-container fluid v-if="!loading">
        <b-row>
          <b-col lg=5>
            <div class="print-info">
              <div class="card-container header">
                <div class="info">
                  <div class="status" :class="print.status.key">{{ print.status.title }}</div>
                  <div class="date">{{ print.ended_at ? print.ended_at.fromNow() : '-' }}</div>
                </div>
              </div>
              <div class="card-container printer">
                <div class="icon">
                  <svg width="1em" height="1em" style="margin-bottom: 5px">
                    <use href="#svg-3d-printer" />
                  </svg>
                </div>
                <div class="info overflow-truncated-parent">
                  <div class="title overflow-truncated">{{ printer.name }}</div>
                  <div class="subtitle overflow-truncated" :class="printer.availabilityStatus().key">
                    {{ printer.availabilityStatus().title }}
                  </div>
                </div>
                <div class="action">
                  <button
                    class="btn btn-primary"
                    :disabled="printer.availabilityStatus().key !== PrinterStatus.Ready.key"
                    @click="onRepeatPrintClicked"
                  >
                    <b-spinner small v-if="isSending" />
                    <span v-else>Repeat print</span>
                  </button>
                </div>
              </div>
              <div class="card-container file">
                <div class="icon">
                  <i class="fas fa-file-code"></i>
                </div>
                <div class="info overflow-truncated-parent">
                  <div class="title overflow-truncated">{{ print.filename }}</div>
                  <div class="subtitle text-secondary overflow-truncated">
                    <span>{{ print.g_code_file.filesize }}</span>
                    <span v-if="print.g_code_file.created_at">, created {{ print.g_code_file.created_at.fromNow() }}</span>
                  </div>
                </div>
                <div class="action">
                  <a class="btn btn-secondary" :href="`/g_code_files/cloud/${print.g_code_file.id}/`">Open file</a>
                </div>
              </div>
              <div class="card-container">
                <div class="info-line">
                  <div class="title">Start time</div>
                  <div class="value">{{ print.started_at.format(absoluteDateFormat) }}</div>
                </div>
                <div class="info-line">
                  <div class="title">End time</div>
                  <div class="value">{{ print.ended_at ? print.ended_at.format(absoluteDateFormat) : '-' }}</div>
                </div>
                <div class="info-line">
                  <div class="title">Duration</div>
                  <div class="value">{{ print.duration ? print.duration : '-' }}</div>
                </div>
              </div>
            </div>
          </b-col>
          <b-col lg=7 class="mt-3 mt-lg-0">
            <div class="time-lapse">
              <div class="card-container" v-if="print.video_archived_at">
                <h2 class="title">Time-Lapse video deleted</h2>
                <p>Time-lapse videos older than 6-months are deleted from the Obico app server as they are rarely needed and cost significant amount to store in the cloud.</p>
                <p>If you are a Pro subscriber and you don't want your time-lapse videos to be deleted, please <a href="mailto:support@obico.io?subject=Please%20keep%20my%20timelapse%20videos">contact us</a>.</p>
              </div>
              <div v-else-if="print.video_url || print.tagged_video_url">
                <b-card no-body>
                  <b-tabs pills card>
                    <b-tab title="Detective Time-Lapse" :disabled="!canShowDetectiveView">
                      <b-card-text>
                        <div v-if="print.tagged_video_url">
                          <div class="video-wrapper">
                            <video-box
                              :videoUrl="print.tagged_video_url"
                              :posterUrl="print.poster_url"
                              :fluid="false"
                              @timeupdate="onTimeUpdate"
                              :fullscreenBtn="false"
                              :defaultFullScreenToggle="true"
                              :downloadBtn="true"
                              @download="() => downloadFile(print.tagged_video_url, `${print.id}_tagged.mp4`)"
                            />
                          </div>
                          <div class="detective-footer">
                            <gauge
                              v-if="print.prediction_json_url"
                              :normalizedP="normalizedP"
                            />
                            <div class="feedback-section">
                              <div class="lead" :class="[print.alerted_at ? 'text-danger' : 'text-success' ]">
                                {{ print.alerted_at ? 'Failure detected' : 'No failure detected' }}
                              </div>
                              <div class="py-2">
                                Did we get it right?
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
                                  <b-button variant="outline-primary" size="sm" :href="focusedFeedbackLink">
                                    <i class="fas fa-check mr-2" v-if="focusedFeedbackCompleted"></i>
                                    FOCUSED FEEDBACK
                                  </b-button>
                                </div>
                              </transition>

                              <div class="about-feedback">
                                <small v-if="focusedFeedbackEligible">
                                  <span v-if="focusedFeedbackCompleted">
                                    Thank you for completing the Focused Feedback. You have earned 2 non-expirable AI Detection Hours. You can click the button again to change your feedback.
                                  </span>
                                  <span v-else>
                                    With Focused Feedback, you can tell us exactly where we got it wrong. This is the most effective way to help us improve.
                                    <a href="https://www.obico.io/docs/user-guides/how-does-credits-work#you-earn-detective-hours-for-giving-focused-feedback" target="_blank">
                                      You will earn 2 AI Detection Hours once you finish the Focused Feedback
                                    </a>
                                  </span>
                                </small>
                                <small v-else>
                                  Every time you give us feedback,
                                  <a href="https://www.obico.io/docs/user-guides/how-does-credits-work/" target="_blank">
                                    you help us get better at detecting failures
                                  </a>
                                </small>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div v-else>
                          <detective-working class="detective-placeholder" />
                        </div>
                      </b-card-text>
                    </b-tab>
                    <b-tab v-if="print.video_url" :active="!print.tagged_video_url" title="Original Time-Lapse">
                      <b-card-text> 
                        <div class="video-wrapper">
                          <video-box
                            :videoUrl="print.video_url"
                            :posterUrl="print.poster_url"
                            :fluid="false"
                            @timeupdate="onTimeUpdate"
                            :fullscreenBtn="false"
                            :defaultFullScreenToggle="true"
                            :downloadBtn="true"
                            @download="() => downloadFile(print.video_url, `${print.id}.mp4`)"
                          />
                        </div>
                      </b-card-text>
                    </b-tab>
                  </b-tabs>
                </b-card>
              </div>
              <div v-else class="card-container">
                <p class="text-secondary text-center mt-3">Time-Lapse video unavailable</p>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'
import { getNormalizedP, downloadFile } from '@src/lib/utils'
import urls from '@config/server-urls'
import { normalizedPrint, PrintStatus, PrinterStatus, normalizedPrinter } from '@src/lib/normalizers'
import PrintCard from '@src/components/prints/PrintCard.vue'
import Layout from '@src/components/Layout.vue'
import VideoBox from '@src/components/VideoBox'
import DetectiveWorking from '@src/components/DetectiveWorking'
import Gauge from '@src/components/Gauge'
import { sendToPrint, showRedirectModal } from '@src/views/gcodes/sendToPrint'

export default {
  name: 'PrintPage',

  components: {
    PrintCard,
    Layout,
    VideoBox,
    DetectiveWorking,
    Gauge,
  },

  props: {
    config: Object
  },

  data: function() {
    return {
      PrintStatus,
      PrinterStatus,
      absoluteDateFormat: 'MMM M, YYYY H:mm A',
      print: null,
      printer: null,
      loading: true,
      isSending: false,
      predictions: [],
      currentPosition: 0,
      inflightAlertOverwrite: null,
      // fullscreenVideoUrl: null,
    }
  },

  created() {
    this.fetchData()
  },

  computed: {
    focusedFeedbackEligible() {
      this.print.printshotfeedback_set.length > 0 && this.print.alert_overwrite
    },

    focusedFeedbackCompleted() {
      return this.print.printshotfeedback_set.length > 0 && !this.print.focusedFeedbackNeeded
    },
    
    normalizedP() {
      return getNormalizedP(this.predictions, this.currentPosition, false)
    },

    canShowDetectiveView() {
      if (
        this.print.prediction_json_url !== null &&
        this.print.tagged_video_url !== null
      ) {
        return true
      }
      // Time-lapses that was uploaded within the past 24 hours are presumably still be processed
      if (
        (this.print.uploaded_at &&
          moment().diff(this.print.uploaded_at, 'hours') < 24)
      ) {
        return true
      }
      return false
    },

    thumbedUp() {
      if (!this.print.alert_overwrite) {
        return false
      }
      return this.print.has_alerts ^ (this.print.alert_overwrite === 'NOT_FAILED')
    },

    thumbedDown() {
      if (!this.print.alert_overwrite) {
        return false
      }
      return this.print.has_alerts ^ (this.print.alert_overwrite === 'FAILED')
    },
  },

  methods: {
    downloadFile,
    fetchData() {
      this.loading = true
      axios.get(urls.print(this.config.printId)).then(response => {
        this.print = normalizedPrint(response.data)
        return axios.get(urls.printer(this.print.printer.id))
      })
      .then((response) => {
        this.printer = normalizedPrinter(response.data)
        return axios.get(this.print.prediction_json_url)
      })
      .then((response) => {
        this.predictions = response.data
        this.loading = false
      })
    },

    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition
    },

    onThumbUpClick() {
      this.inflightAlertOverwrite = this.print.has_alerts ? 'FAILED' : 'NOT_FAILED'
      this.alertOverwrite(this.inflightAlertOverwrite)
    },

    onThumbDownClick() {
      this.inflightAlertOverwrite = this.print.has_alerts ? 'NOT_FAILED' : 'FAILED'
      this.alertOverwrite(this.inflightAlertOverwrite)
    },

    alertOverwrite(value) {
      axios.patch(
        urls.print(this.print.id), {
          alert_overwrite: value,
        })
        .then(response => {
          this.inflightAlertOverwrite = null
          this.fetchData()
        })
    },

    onRepeatPrintClicked() {
      this.isSending = true

      sendToPrint({
        printerId: this.printer.id,
        gcode: this.print.g_code_file,
        isCloud: true,
        Swal: this.$swal,
        onPrinterStatusChanged: () => {
          this.isSending = false
          showRedirectModal(this.$swal, () => this.fetchData())
        }
      })
    }
  }
}
</script>

<style lang="sass" scoped>
.print-info
  display: flex
  flex-direction: column
  gap: 15px

.header
  .date
    font-size: 1.125rem
  .status
    font-weight: bold
    font-size: .875rem
    &.failed
      color: var(--color-danger)
    &.finished
      color: var(--color-success)

.printer, .file
  display: flex
  align-items: center
  gap: 6px
  .info
    flex: 1
  .icon
    flex: 0 0 50px
    text-align: center
    *
      font-size: 2rem

.printer .info .subtitle
    &.ready
      color: var(--color-success)
    &.unavailable
      color: var(--color-warning)

.info-line
  display: flex
  flex-direction: row
  justify-content: space-between
  border-bottom: 1px solid var(--color-divider-muted)
  padding: 4px 0
  &:last-child
    border-bottom: none
.title 
  font-weight: bold

.time-lapse
  .title
    font-size: 1.5rem
    font-weight: normal
    margin-bottom: 1rem

  ::v-deep
    .card
      border-radius: var(--border-radius-lg)
      border: none
      background-color: var(--color-surface-secondary)
    .nav-pills .nav-link
      border-radius: var(--border-radius-sm)
    .nav-pills .nav-link.active
      background-color: var(--color-surface-primary)
    .card-header
      border-bottom: 1px solid var(--color-divider-muted)

.video-wrapper
  border-radius: var(--border-radius-md)
  overflow: hidden

  ::v-deep .video-js
    height: 500px !important

.detective-footer
  margin-top: 30px

.feedback-section
  margin-top: 30px
  text-align: center

.about-feedback
  max-width: 600px
  display: inline-block
  margin-top: 30px

.detective-placeholder
  border-radius: var(--border-radius-md)
  overflow: hidden
</style>
