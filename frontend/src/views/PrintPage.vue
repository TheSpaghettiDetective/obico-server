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
                      <div class="title">{{ $t("Status") }}</div>
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
                      <div class="title">{{ $t("Start time") }}</div>
                    </div>
                    <div class="value">{{ print.started_at.format(absoluteDateFormat) }}</div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="far fa-clock"></i></div>
                      <div class="title">{{ $t("End time") }}</div>
                    </div>
                    <div class="value">
                      {{ print.ended_at ? print.ended_at.format(absoluteDateFormat) : '-' }}
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-clock"></i></div>
                      <div class="title">{{ $t("Duration") }}</div>
                    </div>
                    <div class="value">{{ print.duration || '-' }}</div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-ruler-horizontal"></i></div>
                      <div class="title">{{ $t("Filament used") }}</div>
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
                :show-open-button="canOpenFile"
              />
              <!-- Printer -->
              <div v-if="print.printer" class="card-container printer">
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
                        ? printer.isPrintable() && !printer.inTransientState()
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
                    !print.g_code_file.deleted &&
                    print.g_code_file.url
                  "
                  class="action"
                >
                  <button
                    class="btn btn-primary"
                    :disabled="!printer.isPrintable() || printer.inTransientState()"
                    @click="onRepeatPrintClicked"
                  >
                    <b-spinner v-if="isSending" class="mr-2" small />
                    <span>{{ $t("Reprint") }}</span>
                  </button>
                </div>
              </div>
              <div v-else="print.printer" class="card-container printer">
                <p>Unknown Printer</p>
              </div>

            </div>
          </b-col>
          <b-col lg="7">
            <div class="print-info">
              <!-- First Layer Report Card -->
              <div v-if="firstLayerInspection.id" class="card-container">
                <b-row class="m-0">
                  <b-col cols="12" sm="6" md="6" lg="12" xl="6"   class="first-layer-info-column">
                    <div>
                      <b-row class="mb-4">
                        <span class="ml-3">{{ $t("First Layer Report") }}</span>
                      </b-row>
                      <div class="first-layer-info-line">
                        <div class="label">
                          <div class="icon"><i class="fas fa-info"></i></div>
                          <div class="title">{{ $t("First Layer Grade") }}</div>
                        </div>
                        <div class="value">
                          <div class="print-status-color" :class="gradeResult.gradeAccent">
                            {{ gradeResult.gradeTitle || '&nbsp;' }}
                          </div>
                        </div>
                      </div>
                      <div class="first-layer-info-line">
                        <div class="label">
                          <div class="icon"><i class="far fa-clock"></i></div>
                          <div class="title">{{ $t("First Layer Print Time") }}</div>
                        </div>
                        <div class="value">{{ firstLayerPrintTime }}</div>
                      </div>
                    </div>
                    <b-row class="m-0">
                      <b-button class="open-detailed-report-button" @click="onOpenDetailedReport"
                        >{{ $t("Open Detailed Report") }}</b-button
                      >
                    </b-row>
                  </b-col>
                  <b-col cols="12" sm="6" md="6" lg="12" xl="6" class="first-layer-report-block-video-container">
                    <div class="first-layer-video-wrapper" :class="{
                              'is-fullscreen original':
                                !!fullscreenUrl && fullscreenUrl === firstLayerInspection.tagged_video_url,
                            }">
                      <video-box
                        :video-url="firstLayerInspection.tagged_video_url"
                        :poster-url="aiTimeLapsePosterImageUrl"
                        :fluid="false"
                        :fullscreen-btn="fullscreenUrl === null"
                        :exit-fullscreen-btn="fullscreenUrl !== null"
                        :download-btn="true"
                        @fullscreen="() => enterFullscreen(firstLayerInspection.tagged_video_url)"
                        @exitFullscreen="exitFullscreen"
                        @download="
                          () => downloadFile(firstLayerInspection.tagged_video_url, `${print.id}_tagged_video_inspection.mp4`)
                        "
                      />
                    </div>
                  </b-col>
                </b-row>
              </div>

              <div class="time-lapse">
                <div v-if="print.video_archived_at" class="card-container">
                  <h2 class="title">{{ $t("Time-Lapse video deleted") }}</h2>
                  <p>
                    {{ $t("Time-lapse videos older than 6-months are deleted from the {brandName} app server as they are rarely needed and cost significant amount to store in the cloud.",{brandName:$syndicateText.brandName}) }}
                  </p>
                  <p>
                    <i18next :translation="$t(`If you are a Pro subscriber and you don't want your time-lapse videos to be deleted, please {localizedDom}`)">
                      <template #localizedDom>
                        <a href="mailto:support@obico.io?subject=Please%20keep%20my%20timelapse%20videos">{{$t("contact us")}}</a>
                      </template>
                    </i18next>
                    .
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
                                  {{$t("Did we get it right?")}}
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
                                      {{$t("FOCUSED FEEDBACK")}}
                                    </b-button>
                                  </div>
                                </transition>

                                <div class="about-feedback">
                                  <small v-if="print.printShotFeedbackEligible">
                                    <span v-if="!print.need_print_shot_feedback">
                                      {{$t("Thank you for completing the Focused Feedback. You have earned 2 non-expirable AI Detection Hours. You can click the button again to change your feedback.")}}
                                    </span>
                                    <span v-else>
                                      {{$t("With Focused Feedback, you can tell us exactly where we got it wrong. This is the most effective way to help us improve.")}}
                                      <a
                                        :href="getDocUrl('/user-guides/how-does-credits-work#you-earn-detective-hours-for-giving-focused-feedback')"
                                        target="_blank"
                                      >
                                        {{$t("You will earn 2 AI Detection Hours once you finish the Focused Feedback")}}
                                      </a>
                                    </span>
                                  </small>
                                  <small v-else>
                                    {{$t("Every time you give us feedback,")}}
                                    <a
                                      :href="getDocUrl('/user-guides/how-does-credits-work/')"
                                      target="_blank"
                                    >
                                      {{$t("you help us get better at detecting failures")}}
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
                  <p class="text-secondary mt-3">{{ $t("Time-Lapse video unavailable because") }}:</p>
                  <ul>
                    <li class="text-secondary mt-3">
                      {{ $t("The {brandName} server is still processing the time-lapse;",{brandName:$syndicateText.brandName}) }}
                    </li>
                    <li class="text-secondary mt-3">
                      <i18next :translation="$t(`Or, the print time was shorter than the threshold. You can change the threshold in {localizedDom}`)">
                        <template #localizedDom>
                          <a :href="`/printers/${print.printer.id}/`">{{$t("the printer settings")}}.</a>
                        </template>
                      </i18next>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import { humanizedDuration } from '@src/lib/formatters'
import axios from 'axios'
import moment from 'moment'
import { getNormalizedP, downloadFile } from '@src/lib/utils'
import urls from '@config/server-urls'
import { getLocalPref } from '@src/lib/pref'
import { humanizedFilamentUsage } from '@src/lib/formatters'
import { user, settings } from '@src/lib/page-context'
import { normalizedPrint, PrintStatus, normalizedPrinter, toMomentOrNull } from '@src/lib/normalizers'
import PageLayout from '@src/components/PageLayout.vue'
import VideoBox from '@src/components/VideoBox'
import DetectiveWorking from '@src/components/DetectiveWorking'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'
import { sendToPrint, showRedirectModal, confirmPrint } from '@src/components/g-codes/sendToPrint'
import { restoreFilterValues, getFilterParams } from '@src/components/FilteringDropdown'
import { restoreSortingValue } from '@src/components/SortingDropdown'
import {
  FilterOptions,
  FilterLocalStoragePrefix,
  SortingLocalStoragePrefix,
  SortingOptions,
} from '@src/views/PrintHistoryPage'
import GCodeDetails from '@src/components/GCodeDetails.vue'
import { printerCommManager } from '@src/lib/printer-comm'
import FirstLayerReportModal from '@src/components/prints/FirstLayerReportModal.vue'
import { calculateGrade } from '../services/gradeCalculator';

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
      image: '',
      gradeResult: {},
      firstLayerInspection: {},
      isFirstLayerReportModalOpen: false,
      PrintStatus,
      absoluteDateFormat: 'MMM D, YYYY h:mm a',
      print: null,
      predictions: [],
      printer: null,
      isLoading: true,
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

      printerStateCheckInterval: null,
      firstLayerPrintTime: '-'
    }
  },

  computed: {
    aiTimeLapsePosterImageUrl() {
      if (this.firstLayerInspection.poster_url) {
        return this.firstLayerInspection.poster_url
      }
      return this.firstLayerInspection.images?.length ? this.firstLayerInspection.images[0].image_url : null
    },
    canOpenFile() {
      return this.print.g_code_file &&
            !this.print.g_code_file.resident_printer &&
            !this.print.g_code_file.deleted
    },
    PrevPrintButtonTitle() {
      return this.sortingValue.direction.key === 'asc' ? `${this.$i18next.t('Older')}` : `${this.$i18next.t('Newer')}`
    },
    NextPrintButtonTitle() {
      return this.sortingValue.direction.key === 'asc' ? `${this.$i18next.t('Newer')}` : `${this.$i18next.t('Older')}`
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
    isSending() {
      const printerState = this.printer?.calculatedState()
      return printerState && ['G-Code Downloading', 'Starting'].includes(printerState)
    },
  },

  created() {
    const { IS_ENT } = settings()
    this.isEnt = !!IS_ENT

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

  unmounted() {
    clearInterval(this.printerStateCheckInterval)
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

        this.prepareFirstLayerReport(printResponse.data.firstlayerinspection_set.length ? printResponse.data.firstlayerinspection_set[0] : {})

        if (this.print.prediction_json_url) {
          axios.get(this.print.prediction_json_url).then((response) => {
            this.predictions = response.data
          })
        }

        axios
          .get(urls.printer(this.print.printer.id), { params: { with_archived: true } })
          .then((response) => {
            this.printer = normalizedPrinter(response.data)

            this.printerComm = printerCommManager.getOrCreatePrinterComm(
              this.printer.id,
              urls.printerWebSocket(this.printer.id),
              {
                onPrinterUpdateReceived: (data) => {
                  this.printer = normalizedPrinter(data, this.printer)
                },
              }
            )
            this.printerComm.connect()
          })
          .catch((error) => {
            // Printer could be old and deleted from account (404 error)
            this.printer = null
            if (error?.response?.status !== 404) {
              this.errorDialog(error, `${this.$i18next.t('Failed to fetch printer information')}`)
            }
          })
          .finally(() => {
            this.isLoading = false
          })
      } catch (error) {
        console.log(error)
        this.isLoading = false
      }
    },
    prepareFirstLayerReport(firstLayerInspectionData) {
      this.firstLayerInspection = firstLayerInspectionData;
      if (firstLayerInspectionData.id) {
        this.gradeResult = calculateGrade(firstLayerInspectionData.score);
        const createdAt = toMomentOrNull(this.firstLayerInspection.created_at)
        const duration = moment.duration(createdAt.diff(this.print.started_at))
        this.firstLayerPrintTime = humanizedDuration(duration.asSeconds())
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
          this.errorDialog(error)
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
      confirmPrint(this.print.g_code_file, this.printer).then(() => {
        sendToPrint({
          printer: this.printer,
          gcode: this.print.g_code_file,
          isCloud: this.print.g_code_file?.resident_printer === null,
          Swal: this.$swal,
          onPrinterStatusChanged: () => {
            showRedirectModal(this.$swal, () => this.fetchData(), this.printer.id)
          },
        })
      })
    },
    enterFullscreen(url) {
      this.fullscreenUrl = url
    },
    exitFullscreen() {
      this.fullscreenUrl = null
    },
    onOpenDetailedReport() {
      this.$swal.openModalWithComponent(
        FirstLayerReportModal,
        {
          printer: this.printer,
          firstLayerInspection: this.firstLayerInspection,
          firstLayerPrintTime: this.firstLayerPrintTime,
          gradeResult: this.gradeResult,
          print: this.print,
          showOpenButton: this.canOpenFile
        },
        {
          showCloseButton: true,
          showConfirmButton: false,
          width: '75em'
        }
      )
    },
  },
}
</script>

<style lang="sass" scoped>
.fade-enter-active, .fade-leave-active
  transition: opacity 0.5s
.fade-enter, .fade-leave-to
  opacity: 0
.first-layer-info-column
  display: flex
  flex-direction: column
  justify-content: space-between
  height: 240px
  padding: 0
  @media (max-width: 576px)
    height: auto
    gap: 1em
  @media (max-width: 1198px) and (min-width: 991px)
    height: auto
    gap: 1em
.open-detailed-report-button
  width: 100%

.first-layer-report-block-video-container
  display: flex
  justify-content: flex-end
  padding-right: 0
  @media (max-width: 576px)
    padding: 0
    margin-top: 1em
    justify-content: center
  @media (max-width: 577px) and (max-width: 767px)
    padding: 0 0 0 5px
    justify-content: center
  @media (max-width: 1198px) and (min-width: 991px)
    margin-top: 1em
    padding: 0
    justify-content: center
.heatmap-image-container
  border-radius: var(--border-radius-lg)
  background: white
  padding: 32px
  @media (max-width: 576px)
    height: 393px
    width: 100%
    margin-top: 1.4em
  @media (max-width: 991px) and (min-width: 577px)
    width: 15em
  @media (max-width: 1198px) and (min-width: 992px)
    height: 393px
    width: 100%
    margin-top: 0.5em
  @media (min-width: 1199px)
    width: 15em

.heatmap-image
  border: 1px solid #cac8c8
  height: 176px

  @media (max-width: 576px)
    height: 330px
    width: 100%
  @media (max-width: 1198px) and (min-width: 991px)
    height: 100%
    width: 100%

.first-layer-print-time
  width:100%
  display: flex
  justify-content: space-between
  padding: 0 1em
  grid-template-columns: 3% 67% 30%
  .icon
    flex: 1
    display: flex
    align-items: center
    justify-content: center
    opacity: 0.5
  .name
    flex: 12
    @media (max-width: 768px)
      flex: 15
  .status
    display: flex
    justify-content: flex-end
.first-layer-grade
  width:100%
  display: flex
  justify-content: space-between
  align-items: center
  padding: 0 1em
  .icon
    flex: 1
    display: flex
    align-items: center
    justify-content: center
    opacity: 0.5
  .name
    flex: 7
    @media (max-width: 768px)
      flex: 11
  .status
    display: flex
    justify-content: flex-end

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

.first-layer-info-line
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
  margin-bottom: var(--gap-between-blocks)
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

.first-layer-video-wrapper.is-fullscreen
  flex: 1
  order: 1
  ::v-deep .video-js
    height: 100vh !important

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
