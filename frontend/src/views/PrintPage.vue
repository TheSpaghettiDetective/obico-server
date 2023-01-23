<template>
  <page-layout>
    <template #content>
      <loading-placeholder v-if="isLoading" />
      <b-container v-else fluid>
        <b-row>
          <b-col lg="5">
            <div class="print-info">
              <div class="card-container header">
                <div class="info">
                  <div class="status" :class="print.status.key">
                    {{ print.status.title }}
                  </div>
                  <div class="date">
                    {{ print.ended_at ? print.ended_at.fromNow() : '-' }}
                  </div>
                </div>
              </div>
              <!-- Printer -->
              <div class="card-container printer">
                <div class="icon">
                  <svg width="1em" height="1em" style="margin-bottom: 5px">
                    <use href="#svg-3d-printer" />
                  </svg>
                </div>
                <div class="info overflow-truncated-parent">
                  <div class="title overflow-truncated">{{ print.printer.name }}</div>
                  <div
                    class="subtitle overflow-truncated"
                    :class="[
                      printer
                        ? printer.isPrintable()
                          ? 'text-success'
                          : 'text-warning'
                        : 'text-danger',
                    ]"
                  >
                    {{ printer ? printer.printabilityText() : 'Deleted' }}
                  </div>
                </div>
                <div v-if="printer" class="action">
                  <button
                    class="btn btn-primary"
                    :disabled="!printer.isPrintable()"
                    @click="onRepeatPrintClicked"
                  >
                    <b-spinner v-if="isSending" small />
                    <span v-else>Repeat print</span>
                  </button>
                </div>
              </div>
              <!-- File -->
              <div class="card-container file">
                <div class="icon">
                  <i class="fas fa-file-code"></i>
                </div>
                <div class="info overflow-truncated-parent">
                  <div class="title overflow-truncated">{{ print.filename }}</div>
                  <div v-if="print.g_code_file" class="subtitle text-secondary overflow-truncated">
                    <span>{{ print.g_code_file.filesize }}</span>
                    <span v-if="print.g_code_file.created_at"
                      >, created {{ print.g_code_file.created_at.fromNow() }}</span
                    >
                  </div>
                </div>
                <div v-if="print.g_code_file" class="action">
                  <a
                    class="btn btn-secondary"
                    :href="`/g_code_files/cloud/${print.g_code_file.id}/`"
                    >Open file</a
                  >
                </div>
              </div>
              <div class="card-container">
                <div class="info-line">
                  <div class="title">Start time</div>
                  <div class="value">{{ print.started_at.format(absoluteDateFormat) }}</div>
                </div>
                <div class="info-line">
                  <div class="title">End time</div>
                  <div class="value">
                    {{ print.ended_at ? print.ended_at.format(absoluteDateFormat) : '-' }}
                  </div>
                </div>
                <div class="info-line">
                  <div class="title">Duration</div>
                  <div class="value">{{ print.duration ? print.duration : '-' }}</div>
                </div>
              </div>
            </div>
          </b-col>
          <b-col lg="7" class="mt-3 mt-lg-0">
            <div class="time-lapse">
              <div v-if="print.video_archived_at" class="card-container">
                <h2 class="title">Time-Lapse video deleted</h2>
                <p>
                  Time-lapse videos older than 6-months are deleted from the Obico app server as
                  they are rarely needed and cost significant amount to store in the cloud.
                </p>
                <p>
                  If you are a Pro subscriber and you don't want your time-lapse videos to be
                  deleted, please
                  <a href="mailto:support@obico.io?subject=Please%20keep%20my%20timelapse%20videos"
                    >contact us</a
                  >.
                </p>
              </div>
              <div v-else-if="print.video_url || print.tagged_video_url">
                <b-card no-body>
                  <b-tabs pills card>
                    <b-tab title="Detective Time-Lapse" :disabled="!canShowDetectiveView">
                      <b-card-text>
                        <div
                          v-if="print.tagged_video_url"
                          :class="{
                            'is-fullscreen':
                              !!fullscreenUrl && fullscreenUrl === print.tagged_video_url,
                          }"
                        >
                          <div class="video-wrapper">
                            <video-box
                              :video-url="print.tagged_video_url"
                              :poster-url="print.poster_url"
                              :fluid="false"
                              :fullscreen-btn="fullscreenUrl === null"
                              :exit-fullscreen-btn="fullscreenUrl !== null"
                              :download-btn="true"
                              @timeupdate="onTimeUpdate"
                              @fullscreen="() => enterFullscreen(print.tagged_video_url)"
                              @exitFullscreen="exitFullscreen"
                              @download="
                                () => downloadFile(print.tagged_video_url, `${print.id}_tagged.mp4`)
                              "
                            />
                          </div>
                          <div class="detective-footer">
                            <failure-detection-gauge
                              v-if="print.prediction_json_url"
                              :normalized-p="normalizedP"
                            />
                            <div class="feedback-section">
                              <div
                                class="lead"
                                :class="[print.alerted_at ? 'text-danger' : 'text-success']"
                              >
                                {{ print.alerted_at ? 'Failure detected' : 'No failure detected' }}
                              </div>
                              <div class="py-2">
                                Did we get it right?
                                <b-button
                                  :variant="thumbedUp ? 'primary' : 'outline'"
                                  class="mx-2 btn-sm"
                                  @click="onThumbUpClick"
                                >
                                  <b-spinner
                                    v-if="inflightAlertOverwrite"
                                    type="grow"
                                    small
                                  ></b-spinner>
                                  <i v-else class="fas fa-thumbs-up"></i>
                                </b-button>
                                <b-button
                                  :variant="thumbedDown ? 'primary' : 'outline'"
                                  class="mx-2 btn-sm"
                                  @click="onThumbDownClick"
                                >
                                  <b-spinner
                                    v-if="inflightAlertOverwrite"
                                    type="grow"
                                    small
                                  ></b-spinner>
                                  <i v-else class="fas fa-thumbs-down"></i>
                                </b-button>
                              </div>
                              <transition name="bounce">
                                <div v-if="print.printShotFeedbackEligible" class="pt-2">
                                  <b-button
                                    variant="outline-primary"
                                    size="sm"
                                    :href="`/prints/shot-feedback/${print.id}/`"
                                    target="_blank"
                                  >
                                    <i
                                      v-if="!print.need_print_shot_feedback"
                                      class="fas fa-check mr-2"
                                    ></i>
                                    FOCUSED FEEDBACK
                                  </b-button>
                                </div>
                              </transition>

                              <div class="about-feedback">
                                <small v-if="print.printShotFeedbackEligible">
                                  <span v-if="!print.need_print_shot_feedback">
                                    Thank you for completing the Focused Feedback. You have earned 2
                                    non-expirable AI Detection Hours. You can click the button again
                                    to change your feedback.
                                  </span>
                                  <span v-else>
                                    With Focused Feedback, you can tell us exactly where we got it
                                    wrong. This is the most effective way to help us improve.
                                    <a
                                      href="https://www.obico.io/docs/user-guides/how-does-credits-work#you-earn-detective-hours-for-giving-focused-feedback"
                                      target="_blank"
                                    >
                                      You will earn 2 AI Detection Hours once you finish the Focused
                                      Feedback
                                    </a>
                                  </span>
                                </small>
                                <small v-else>
                                  Every time you give us feedback,
                                  <a
                                    href="https://www.obico.io/docs/user-guides/how-does-credits-work/"
                                    target="_blank"
                                  >
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
                    <b-tab
                      v-if="print.video_url"
                      :active="!print.tagged_video_url"
                      title="Original Time-Lapse"
                    >
                      <b-card-text>
                        <div
                          :class="{
                            'is-fullscreen original':
                              !!fullscreenUrl && fullscreenUrl === print.video_url,
                          }"
                        >
                          <div class="video-wrapper">
                            <video-box
                              :video-url="print.video_url"
                              :poster-url="print.poster_url"
                              :fluid="false"
                              :fullscreen-btn="fullscreenUrl === null"
                              :exit-fullscreen-btn="fullscreenUrl !== null"
                              :download-btn="true"
                              @timeupdate="onTimeUpdate"
                              @fullscreen="() => enterFullscreen(print.video_url)"
                              @exitFullscreen="exitFullscreen"
                              @download="() => downloadFile(print.video_url, `${print.id}.mp4`)"
                            />
                          </div>
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
  </page-layout>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import { getNormalizedP, downloadFile } from '@src/lib/utils'
import urls from '@config/server-urls'
import { normalizedPrint, PrintStatus, normalizedPrinter } from '@src/lib/normalizers'
import PageLayout from '@src/components/PageLayout.vue'
import VideoBox from '@src/components/VideoBox'
import DetectiveWorking from '@src/components/DetectiveWorking'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'
import { sendToPrint, showRedirectModal } from '@src/components/g-codes/sendToPrint'

export default {
  name: 'PrintPage',

  components: {
    PageLayout,
    VideoBox,
    DetectiveWorking,
    FailureDetectionGauge,
  },

  props: {
    printId: {
      type: Number,
      required: true,
    },
  },

  data: function () {
    return {
      PrintStatus,
      absoluteDateFormat: 'MMM M, YYYY H:mm A',
      data: {
        print: undefined,
        predictions: undefined,
        printer: undefined,
      },
      isSending: false,
      currentPosition: 0,
      inflightAlertOverwrite: null,
      fullscreenUrl: null,
    }
  },

  computed: {
    // shortcuts
    print() {
      return this.data.print
    },
    predictions() {
      return this.data.predictions
    },
    printer() {
      return this.data.printer
    },

    isLoading() {
      return !!Object.values(this.data).filter((d) => d === undefined).length
    },

    normalizedP() {
      return getNormalizedP(this.predictions, this.currentPosition, false)
    },

    canShowDetectiveView() {
      if (this.print.prediction_json_url !== null && this.print.tagged_video_url !== null) {
        return true
      }
      // Time-lapses that was uploaded within the past 24 hours are presumably still be processed
      if (this.print.uploaded_at && moment().diff(this.print.uploaded_at, 'hours') < 24) {
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

  created() {
    this.fetchData()
  },

  mounted() {
    const exitFullscreen = this.exitFullscreen
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        exitFullscreen()
      }
    })
  },

  methods: {
    downloadFile,
    async fetchData(clearPreviousData = true) {
      if (clearPreviousData) {
        for (const key of Object.keys(this.data)) {
          this.data[key] = undefined
        }
      }

      try {
        const printResponse = await axios.get(urls.print(this.printId))
        this.data.print = normalizedPrint(printResponse.data)

        axios.get(this.print.prediction_json_url).then((response) => {
          this.data.predictions = response.data
        })

        axios
          .get(urls.printer(this.print.printer.id))
          .then((response) => {
            this.data.printer = normalizedPrinter(response.data)
          })
          .catch((error) => {
            // Printer could be old and deleted from account (404 error)
            this.data.printer = null
            if (error?.response?.status !== 404) {
              this._showErrorPopup(error, 'Failed to fetch printer information')
            }
          })
      } catch (error) {
        this._showErrorPopup(error)
      }
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
      axios
        .patch(urls.print(this.print.id), {
          alert_overwrite: value,
        })
        .then((response) => {
          this.inflightAlertOverwrite = null
          this.fetchData(false)
        })
    },
    onRepeatPrintClicked() {
      this.isSending = true

      sendToPrint({
        printerId: this.printer.id,
        gcode: this.print.g_code_file,
        isCloud: true,
        isAgentMoonraker: this.printer.isAgentMoonraker(),
        Swal: this.$swal,
        onPrinterStatusChanged: () => {
          this.isSending = false
          showRedirectModal(this.$swal, () => this.fetchData())
        },
      })
    },
    enterFullscreen(url) {
      this.fullscreenUrl = url
    },
    exitFullscreen() {
      this.fullscreenUrl = null
    },
  },
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
    &.cancelled
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

  ::v-deep video:focus-visible
    outline: none !important
    box-shadow: none !important
    border: none !important

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

.is-fullscreen
  position: fixed
  top: 0
  left: 0
  bottom: 0
  right: 0
  z-index: 9999
  background-color: var(--color-background)
  padding: 1rem
  display: flex

  .video-wrapper
    flex: 1
    order: 1
    ::v-deep .video-js
      height: calc(100vh - 2rem) !important

  .detective-footer
    flex: 0 0 200px
    padding: 0 1rem
    display: flex
    flex-direction: column
    justify-content: center
    position: relative

  @media (max-width: 996px)
    flex-direction: column

    .video-wrapper
      order: 0
      flex: 0 0 400px
      ::v-deep .video-js
        height: 400px !important

    .detective-footer
      flex: 1
      .feedback-section
        display: none

  &.original
    padding: 0

    .video-wrapper
      flex: 1 !important
      border-radius: 0
      ::v-deep .video-js
        height: 100vh !important
</style>
