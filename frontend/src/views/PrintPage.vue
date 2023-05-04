<template>
  <page-layout>
    <template #content>
      <loading-placeholder v-if="isLoading" />
      <b-container v-else fluid>
        <b-row>
          <b-col lg="5">
            <div class="print-info">
              <!-- Print details -->
              <div class="card-container print-details">
                <div v-if="currentIndex || currentIndex === 0" class="navigation-container">
                  <b-button
                    variant="outline-secondary"
                    :disabled="!prevPrint"
                    @click.prevent="switchToPrint(prevPrint)"
                  >
                    <i class="fas fa-chevron-left"></i>&nbsp;&nbsp;{{ PrevPrintButtonTitle }}
                  </b-button>
                  <div class="summary truncated-wrapper">
                    <div class="date truncated">
                      {{ print.started_at.format(absoluteDateFormat) }}
                    </div>
                  </div>
                  <b-button
                    variant="outline-secondary"
                    :disabled="!nextPrint"
                    @click.prevent="switchToPrint(nextPrint)"
                  >
                    {{ NextPrintButtonTitle }}&nbsp;&nbsp;<i class="fas fa-chevron-right"></i>
                  </b-button>
                </div>
                <div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-info"></i></div>
                      <div class="title">Status</div>
                    </div>
                    <div class="value">
                      <div class="print-status-color" :class="print.status.key">
                        {{ print.status.title }}
                      </div>
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="far fa-clock"></i></div>
                      <div class="title">Start time</div>
                    </div>
                    <div class="value">{{ print.started_at.format(absoluteDateFormat) }}</div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="far fa-clock"></i></div>
                      <div class="title">End time</div>
                    </div>
                    <div class="value">
                      {{ print.ended_at ? print.ended_at.format(absoluteDateFormat) : '-' }}
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-clock"></i></div>
                      <div class="title">Duration</div>
                    </div>
                    <div class="value">{{ print.duration || '-' }}</div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-ruler-horizontal"></i></div>
                      <div class="title">Filament used</div>
                    </div>
                    <div class="value">
                      {{ print.filament_used ? humanizedFilamentUsage(print.filament_used) : '-' }}
                    </div>
                  </div>
                </div>
              </div>
              <!-- GCode details -->
              <g-code-details
                :file="print.g_code_file || { filename: print.filename }"
                :show-open-button="
                  print.g_code_file &&
                  !print.g_code_file.resident_printer &&
                  !print.g_code_file.deleted
                "
              />
              <!-- Printer -->
              <div class="card-container printer">
                <div class="icon">
                  <svg width="1em" height="1em" style="margin-bottom: 5px">
                    <use href="#svg-3d-printer" />
                  </svg>
                </div>
                <div class="info truncated-wrapper">
                  <div class="title truncated" :title="print.printer.name">
                    {{ print.printer.name }}
                  </div>
                  <div
                    class="subtitle truncated"
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
                <div
                  v-if="
                    printer &&
                    print.g_code_file &&
                    !print.g_code_file.resident_printer &&
                    !print.g_code_file.deleted
                  "
                  class="action"
                >
                  <button
                    class="btn btn-primary"
                    :disabled="!printer.isPrintable()"
                    @click="onRepeatPrintClicked"
                  >
                    <b-spinner v-if="isSending" small />
                    <span v-else>Repeat Print</span>
                  </button>
                </div>
              </div>
            </div>
          </b-col>
          <b-col lg="7">
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
                <p class="text-secondary mt-3">Time-Lapse video unavailable because:</p>
                <ul>
                  <li class="text-secondary mt-3">
                    The Obico server is still processing the time-lapse;
                  </li>
                  <li class="text-secondary mt-3">
                    Or, the print time was shorter than the threshold. You can change the threshold
                    in
                    <a :href="`/printers/${print.printer.id}/`">the printer settings.</a>
                  </li>
                </ul>
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
import { getLocalPref } from '@src/lib/pref'
import { humanizedFilamentUsage } from '@src/lib/formatters'
import { user } from '@src/lib/page-context'
import { normalizedPrint, PrintStatus, normalizedPrinter } from '@src/lib/normalizers'
import PageLayout from '@src/components/PageLayout.vue'
import VideoBox from '@src/components/VideoBox'
import DetectiveWorking from '@src/components/DetectiveWorking'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'
import { sendToPrint, showRedirectModal } from '@src/components/g-codes/sendToPrint'
import { restoreFilterValues, getFilterParams } from '@src/components/FilteringDropdown'
import { restoreSortingValue } from '@src/components/SortingDropdown'
import {
  FilterOptions,
  FilterLocalStoragePrefix,
  SortingLocalStoragePrefix,
  SortingOptions,
} from '@src/views/PrintHistoryPage'
import GCodeDetails from '@src/components/GCodeDetails.vue'

export default {
  name: 'PrintPage',

  components: {
    PageLayout,
    VideoBox,
    DetectiveWorking,
    FailureDetectionGauge,
    GCodeDetails,
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
      absoluteDateFormat: 'MMM D, YYYY h:mm a',
      print: null,
      predictions: [],
      printer: null,
      isLoading: true,
      isSending: false,
      currentPosition: 0,
      inflightAlertOverwrite: null,
      fullscreenUrl: null,
      user: null,
      currentPrint: null,

      // Pagination
      prevPrint: null,
      nextPrint: null,
      // Sorting for pagination
      sortingValue: restoreSortingValue(SortingLocalStoragePrefix, SortingOptions),
      // Filtering for pagination
      filterLocalStoragePrefix: FilterLocalStoragePrefix,
      filterOptions: FilterOptions,
      filterValues: restoreFilterValues(FilterLocalStoragePrefix, FilterOptions),
    }
  },

  computed: {
    PrevPrintButtonTitle() {
      return this.sortingValue.direction.key === 'asc' ? 'Older' : 'Newer'
    },
    NextPrintButtonTitle() {
      return this.sortingValue.direction.key === 'asc' ? 'Newer' : 'Older'
    },
    fileName() {
      return this.print.g_code_file === null ? this.print.filename : this.print.g_code_file.filename
    },
    currentPrintId() {
      return this.currentPrint?.id || this.printId
    },
    currentIndex() {
      if (this.currentPrint) {
        return this.currentPrint.index
      }

      const urlParams = new URLSearchParams(window.location.search)
      let indexParam = urlParams.get('index')
      if (!indexParam) {
        return
      }

      return parseInt(indexParam)
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
    this.user = user()
    this.fetchData()
    this.fetchSiblingPrints()
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
    humanizedFilamentUsage,

    async fetchData(clearPreviousData = true) {
      if (clearPreviousData) {
        this.print = null
        this.predictions = []
        this.printer = null
      }

      this.isLoading = true
      try {
        const printResponse = await axios.get(urls.print(this.currentPrintId))
        this.print = normalizedPrint(printResponse.data)

        if (this.print.prediction_json_url) {
          axios.get(this.print.prediction_json_url).then((response) => {
            this.predictions = response.data
          })
        }

        axios
          .get(urls.printer(this.print.printer.id), { params: { with_archived: true } })
          .then((response) => {
            this.printer = normalizedPrinter(response.data)
          })
          .catch((error) => {
            // Printer could be old and deleted from account (404 error)
            this.printer = null
            if (error?.response?.status !== 404) {
              this._logError(error, 'Failed to fetch printer information')
            }
          })
          .finally(() => {
            this.isLoading = false
          })
      } catch (error) {
        console.log(error)
      }
    },
    switchToPrint(print) {
      this.currentPrint = print
      const newUrl = `/prints/${print.id}/?index=${print.index}`
      window.history.replaceState({}, '', newUrl)
      this.fetchData()
      this.fetchSiblingPrints()
    },
    fetchSiblingPrints() {
      if (!this.currentIndex && this.currentIndex !== 0) {
        return
      }

      const prevExists = this.currentIndex > 0
      const start = prevExists ? this.currentIndex - 1 : 0
      const limit = prevExists ? 3 : 2

      axios
        .get(urls.prints(), {
          params: {
            start,
            limit,
            ...getFilterParams(
              this.filterOptions,
              this.filterValues,
              (filterOptionKey, filterValueKey) => {
                if (filterOptionKey === 'timePeriod') {
                  return this.filterOptions[filterOptionKey].buildQueryParam(
                    filterValueKey,
                    getLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateFrom`) || null,
                    getLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateTo`) || null,
                    this.user
                  )
                }
              }
            ),
            sorting: `${this.sortingValue.sorting.key}_${this.sortingValue.direction.key}`,
          },
        })
        .then((response) => {
          const data = response.data
          let prev
          let next
          if (prevExists) {
            if (data.length === 3 && data[1].id === this.currentPrintId) {
              // prev and next exist
              prev = data[0]
              next = data[2]
            } else if (data.length === 2 && data[1].id === this.currentPrintId) {
              // only prev exists
              prev = data[0]
            } else {
              // no prev or next
              return
            }
          } else {
            if (data.length === 2 && data[0].id === this.currentPrintId) {
              // only next exists
              next = data[1]
            } else {
              // no prev or next
              return
            }
          }

          this.prevPrint = prev ? { id: prev.id, index: this.currentIndex - 1 } : null
          this.nextPrint = next ? { id: next.id, index: this.currentIndex + 1 } : null
        })
        .catch((error) => {
          this._logError(error)
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
          showRedirectModal(this.$swal, () => this.fetchData(), this.printer.id)
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
  gap: var(--gap-between-blocks)

.print-details
  overflow: hidden
  display: flex
  flex-direction: column
  gap: 10px
  .navigation-container
    display: flex
    justify-content: space-between
    align-items: center
    gap: 1rem
    margin: -1.5em
    margin-bottom: .5em
    padding: 1em 1.5em
    background-color: var(--color-surface-primary)
    .btn
      flex-shrink: 0
    .summary
      text-align: center
      @media (max-width: 576px)
        display: none
  .info-line
    display: flex
    align-items: center
    justify-content: space-between
    margin-bottm: 6px
    padding: 6px 0
    gap: .5rem
    border-top: 1px solid var(--color-divider-muted)
    &:first-of-type
      border-top: none
    .label
      display: flex
      align-items: center
      flex: 1
      gap: .5rem
      line-height: 1.1
      .icon
        opacity: .5
        width: 1rem
        text-align: center
    .value
      font-weight: bold

.printer
  display: flex
  align-items: center
  gap: .7rem
  .title
    font-weight: bold
  .info
    flex: 1
  .icon
    flex: 0 0 2rem
    text-align: center
    *
      font-size: 2rem

.time-lapse
  .title
    font-size: 1.5rem
    font-weight: normal
    margin-bottom: 1rem
  @media (max-width: 991px)
    margin-top: var(--gap-between-blocks)
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
