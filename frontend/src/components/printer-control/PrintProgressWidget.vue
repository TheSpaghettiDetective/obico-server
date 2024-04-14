<template>
  <widget-template>
    <template #title>{{ isPrinting ? $t('Print Progress') : $t('Last Print') }}</template>
    <template #content>
      <div class="wrapper">
        <template v-if="print">
          <div class="header">
            <g-code-details
              :file="print.g_code_file || { filename: print.filename }"
              :show-open-button="
                print.g_code_file &&
                !print.g_code_file.resident_printer &&
                !print.g_code_file.deleted
              "
              :show-details="false"
              class="g-code-details"
            />
          </div>

          <div class="content">
            <div class="details">
              <!-- Last Print -->
              <template v-if="!isPrinting">
                <div class="info-line no-border">
                  <div class="label">
                    <div class="icon"><i class="fas fa-info"></i></div>
                    <div class="title">{{ $t("Status") }}</div>
                  </div>
                  <div class="value">
                    <div
                      v-if="!print.status.isActive"
                      class="print-status-color"
                      :class="print.status.key"
                    >
                      {{ print.status.title }}
                    </div>
                    <!-- Show loader if printer not marked as ended yet -->
                    <b-spinner v-else small></b-spinner>
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="far fa-clock"></i></div>
                    <div class="title">{{ $t("Started") }}</div>
                  </div>
                  <div class="value">{{ print.started_at.format('MMM D, YYYY h:mm a') }}</div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <div class="title">{{ $t("Duration") }}</div>
                  </div>
                  <div v-if="!print.status.isActive" class="value">
                    {{ print.duration || '-' }}
                  </div>
                  <!-- Show loader if printer not marked as ended yet -->
                  <b-spinner v-else small></b-spinner>
                </div>
              </template>

              <!-- Print Progress -->
              <template v-else>
                <div v-if="isPrinting" class="progress-container">
                  <div class="progress-bar-wrapper">
                    <div
                      class="progress-bar-inner"
                      :style="`width: ${printProgressPercentage}%`"
                    ></div>
                  </div>
                  <div class="percentage-progress">{{ printProgressPercentage }}%</div>
                </div>

                <div class="info-line no-border">
                  <div class="label">
                    <div class="icon"><i class="fas fa-info"></i></div>
                    <div class="title">{{ $t("Status") }}</div>
                  </div>
                  <div class="value" :class="'text-' + printer.calculatedStateColor()">
                    {{ printer.calculatedState() }}
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon">
                      <font-awesome-icon :icon="['fas', 'layer-group']" />
                    </div>
                    <div class="title">{{ $t("Layer") }}</div>
                  </div>
                  <div class="value">
                    {{ layerProgress }}
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon">
                      <i class="fas fa-stopwatch"></i>
                    </div>
                    <div class="title">{{ $t("Remaining") }}</div>
                  </div>
                  <div class="value">
                    <span v-if="secondsLeft">{{ humanizedDuration(secondsLeft) }}</span>
                    <span v-else class="text-secondary">{{ $t("Calculating...") }}</span>
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fas fa-flag-checkered"></i></div>
                    <div class="title">{{ $t("Finishing at") }}</div>
                  </div>
                  <div class="value">
                    <span v-if="finishingAt">{{ finishingAt }}</span>
                    <span v-else class="text-secondary">{{ $t("Calculating...") }}</span>
                  </div>
                </div>
                <collapsable-details>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-clock"></i></div>
                      <div class="title">{{ $t("Started") }}</div>
                    </div>
                    <div class="value">
                      {{ print.started_at.format(DATE_TIME_FORMAT) }}
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon"><i class="fas fa-stopwatch"></i></div>
                      <div class="title">{{ $t("Elapsed") }}</div>
                    </div>
                    <div class="value">
                      <span v-if="timeElapsed">{{ timeElapsed }}</span>
                      <b-spinner v-else small></b-spinner>
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon">
                        <font-awesome-icon :icon="['fas', 'ruler-vertical']" />
                      </div>
                      <div class="title">{{ $t("Z-height") }}</div>
                    </div>
                    <div class="value">
                      {{ mmProgress }}
                    </div>
                  </div>
                  <div class="info-line">
                    <div class="label">
                      <div class="icon">
                        <i class="fas fa-stopwatch"></i>
                      </div>
                      <div class="title">{{ $t("Total time") }}</div>
                    </div>
                    <div v-if="timeTotal" class="value">
                      {{ timeTotal }}
                    </div>
                    <span v-else class="text-secondary">{{ $t("Calculating...") }}</span>
                  </div>
                  <div class="info-line" v-if="print.filament_used">
                    <div class="label">
                      <div class="icon">
                        <font-awesome-icon :icon="['fas', 'ruler-vertical']" />
                      </div>
                      <div class="title">{{ $t("Total filament") }}</div>
                    </div>
                    <div class="value">
                      {{ humanizedFilamentUsage(print.filament_used) }}
                    </div>
                  </div>
                </collapsable-details>
              </template>
            </div>

            <div v-if="!isPrinting" class="actions">
              <b-button
                variant="outline-secondary"
                class="custom-button"
                :href="`/prints/${print.id}`"
              >
                {{$t("Open Print")}}
              </b-button>
              <b-button
                v-if="file.url"
                variant="secondary"
                class="custom-button"
                :disabled="isPrintStarting"
                @click="onRepeatClicked"
              >
                <b-spinner v-if="isPrintStarting" small></b-spinner>
                <i v-else class="fas fa-redo"></i>
                {{$t("Reprint")}}
              </b-button>
            </div>
          </div>
        </template>
        <template v-else>
          <p class="empty-state-text">{{ $t("No prints found") }}</p>
        </template>
      </div>
    </template>
  </widget-template>
</template>

<script>
import moment from 'moment'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import GCodeDetails from '@src/components/GCodeDetails.vue'
import { humanizedDuration, timeFromNow, humanizedFilamentUsage } from '@src/lib/formatters'
import { sendToPrint, confirmPrint } from '@src/components/g-codes/sendToPrint'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import CollapsableDetails from '@src/components/CollapsableDetails.vue'

const DATE_TIME_FORMAT = 'MMM D, h:mm a'

export default {
  name: 'PrintProgressWidget',

  components: {
    WidgetTemplate,
    GCodeDetails,
    CollapsableDetails,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
    print: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      DATE_TIME_FORMAT,
      timeElapsed: null,
      finishingAt: null,
      startedAt: null,
      printProgressPercentage: 0,
      extraVisible: false,
    }
  },

  computed: {
    file() {
      return this.print?.g_code_file || {}
    },
    isPrinting() {
      return this.printer.isActive() && this.printer.progressCompletion() < 100
    },
    isPrintStarting() {
      return this.printer.inTransientState()
    },
    mmProgress() {
      let progressInMillimeters

      const progressMillimeters = this.printer.status?.currentZ
      const totalMillimeters = this.printer.status?.file_metadata?.analysis?.printingArea?.maxZ

      if ((progressMillimeters || progressMillimeters == 0) && totalMillimeters) {
        progressInMillimeters = `${progressMillimeters.toFixed(2)}/${totalMillimeters.toFixed(
          2
        )} mm`
      }

      return progressInMillimeters || '--/--'
    },
    layerProgress() {
      let progressInLayers

      const progressLayers = this.printer.status?.currentLayerHeight
      const totalLayers = this.printer.status?.file_metadata?.obico?.totalLayerCount
      if ((progressLayers || progressLayers == 0) && totalLayers) {
        progressInLayers = `${Math.round(progressLayers)}/${Math.round(totalLayers)}`
      }

      return progressInLayers || '--/--'
    },
    timeTotal() {
      let secs = null
      if (this.secondsPrinted && this.secondsLeft) {
        secs = this.secondsPrinted + this.secondsLeft
        return humanizedDuration(secs)
      }
      return null
    },
    secondsPrinted() {
      return this.printer?.status?.progress?.printTime ?? null
    },
    secondsLeft() {
      return this.printer?.status?.progress?.printTimeLeft ?? null
    },
  },

  watch: {
    printer: {
      handler: function (newValue, oldValue) {
        if (this.isPrinting) {
          this.updatePrintProgress()
        }
      },
      deep: true,
    },
  },

  mounted() {
    if (this.isPrinting) {
      this.updatePrintProgress()
    }
  },

  unmounted() {
    clearInterval(this.printerStateCheckInterval)
  },

  methods: {
    humanizedDuration,
    humanizedFilamentUsage,
    toggleZHeightProgressType() {
      this.preferZHeightProgressInLayers = !this.preferZHeightProgressInLayers
      setLocalPref('preferZHeightProgressInLayers', this.preferZHeightProgressInLayers)
    },
    updatePrintProgress() {
      if (!this.isPrinting) return
      if (!this.print) return

      // Time elapsed
      const elapsed = moment.duration(moment().diff(this.print.started_at))
      this.timeElapsed = this.print.status.isActive ? humanizedDuration(elapsed.asSeconds()) : null

      this.finishingAt =
        typeof this.secondsLeft === 'number'
          ? timeFromNow(this.secondsLeft, DATE_TIME_FORMAT)
          : null

      // Progress bar
      this.printProgressPercentage = Math.round(this.printer.progressCompletion())
      this.printProgressMillimeters = Math.round(this.printer.status?.currentZ || 0)
      this.printMillimetersTotal = Math.round(
        this.printer.status?.file_metadata?.analysis?.printingArea?.maxZ || 0
      )
    },

    onRepeatClicked() {
      if (this.isPrinting) return

      if (!this.print) {
        console.error("Can't repeat last print: no last print")
        return
      }
      if (this.print.g_code_file.deleted) {
        console.error("Can't repeat last print: G-Code deleted")
        return
      }
      if (!this.print.g_code_file.url) {
        // Usually OctoPrint/Klipper files
        console.error("Can't repeat last print: no G-Code file in storage")
        return
      }

      confirmPrint(this.print.g_code_file, this.printer).then(() => {
        sendToPrint({
          printer: this.printer,
          gcode: this.print.g_code_file,
          isCloud: this.print.g_code_file?.resident_printer === null,
          Swal: this.$swal,
        })
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  padding-bottom: 1rem

.header
  margin-bottom: 1rem

.info-line
  display: flex
  align-items: center
  justify-content: space-between
  margin-bottm: 6px
  padding: 6px 0
  gap: .5rem
  border-top: 1px solid var(--color-divider-muted)
  &.no-border
    border-top: none
  .label
    display: flex
    align-items: center
    flex: 1
    gap: .5rem
    line-height: 1.1
    .icon
      width: 1rem
      text-align: center
  .value
    font-weight: bold

.g-code-details
  padding: 0
  width: 100%

.actions
  margin-top: 1rem
  display: flex
  justify-content: center
  gap: 1rem

.progress-container
  font-weight: bold
  margin-bottom: 1rem
  display: flex
  gap: 1rem
  align-items: center
  .progress-bar-wrapper
    height: 12px
    flex: 1
    border-radius: 999px
    background-color: var(--color-background)
    position: relative
    top: 1px
    overflow: hidden
  .progress-bar-inner
    height: 100%
    // border-radius: 999px
    background-color: var(--color-primary)
.empty-state-text
  text-align: center
  font-size: 1.125rem
</style>
