<template>
  <widget-template>
    <template #title>{{ isPrinting ? 'Print Progress' : 'Last Print' }}</template>
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
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fas fa-info"></i></div>
                    <div class="title">Status</div>
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
                    <div class="title">Started</div>
                  </div>
                  <div class="value">{{ print.started_at.format('MMM D, YYYY h:mm a') }}</div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <div class="title">Duration</div>
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
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <div class="title">Elapsed</div>
                  </div>
                  <div class="value">
                    <span v-if="timeElapsed">{{ timeElapsed }}</span>
                    <b-spinner v-else small></b-spinner>
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fa-solid fa-stopwatch"></i></div>
                    <div class="title">Remaining</div>
                  </div>
                  <div class="value">
                    <span v-if="timeRemaining">{{ timeRemaining }}</span>
                    <span v-else class="text-secondary">Calculating...</span>
                  </div>
                </div>
                <div class="info-line">
                  <div class="label">
                    <div class="icon"><i class="fa-solid fa-flag-checkered"></i></div>
                    <div class="title">Finishing At</div>
                  </div>
                  <div class="value">
                    <span v-if="finishingAt">{{ finishingAt }}</span>
                    <span v-else class="text-secondary">Calculating...</span>
                  </div>
                </div>
              </template>
            </div>

            <div v-if="isPrinting" class="progress-container">
              <div class="percentage-progress">{{ printProgressPercentage }}%</div>

              <div class="progress-bar-wrapper">
                <div class="progress-bar-inner" :style="`width: ${printProgressPercentage}%`"></div>
              </div>
              <div v-if="printMillimetersTotal" class="layer-progress">
                <span>{{ printProgressMillimeters }}</span>
                <span> / {{ printMillimetersTotal }}</span>
                <span> mm</span>
              </div>
            </div>
            <div v-else class="actions">
              <b-button
                variant="outline-secondary"
                class="custom-button"
                :href="`/prints/${print.id}`"
              >
                Open Print
              </b-button>
              <b-button
                v-if="file.url"
                variant="secondary"
                class="custom-button"
                :disabled="isPrintStarting"
                @click="onRepeatClicked"
              >
                <b-spinner v-if="isPrintStarting" small></b-spinner>
                <i v-else class="fa-solid fa-rotate-right"></i>
                Repeat
              </b-button>
            </div>
          </div>
        </template>
        <template v-else>
          <p class="empty-state-text">No prints found</p>
        </template>
      </div>
    </template>
  </widget-template>
</template>

<script>
import moment from 'moment'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import GCodeDetails from '@src/components/GCodeDetails.vue'
import { humanizedDuration, timeFromNow } from '@src/lib/formatters'
import { sendToPrint } from '@src/components/g-codes/sendToPrint'

export default {
  name: 'PrintProgressWidget',

  components: {
    WidgetTemplate,
    GCodeDetails,
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
      timeElapsed: null,
      timeRemaining: null,
      finishingAt: null,
      printProgressPercentage: 0,
      printProgressMillimeters: 0,
      printMillimetersTotal: 0,
      isPrintStarting: false,
    }
  },

  computed: {
    file() {
      return this.print?.g_code_file || {}
    },
    thumbnailUrl() {
      let thumbnailProps = ['thumbnail3_url', 'thumbnail2_url', 'thumbnail1_url']
      let result = null
      for (const t of thumbnailProps) {
        if (this.file && this.file[t]) {
          result = this.file[t]
          break
        }
      }
      return result
    },
    isPrinting() {
      return this.printer.isActive() && this.printer.progressCompletion() < 100
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

  methods: {
    updatePrintProgress() {
      if (!this.isPrinting) return
      if (!this.print) return

      // Time elapsed
      const elapsed = moment.duration(moment().diff(this.print.started_at))
      this.timeElapsed = this.print.status.isActive ? humanizedDuration(elapsed.asSeconds()) : null

      // Time remaining and finishing at
      const remaining = this.printer.status?.progress?.printTimeLeft
      this.timeRemaining = typeof remaining === 'number' ? humanizedDuration(remaining) : null
      this.finishingAt = typeof remaining === 'number' ? timeFromNow(remaining) : null

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

      this.isPrintStarting = true

      sendToPrint({
        printerId: this.printer.id,
        gcode: this.print.g_code_file,
        isCloud: true,
        isAgentMoonraker: this.printer.isAgentMoonraker(),
        Swal: this.$swal,
        onPrinterStatusChanged: () => {
          this.isPrintStarting = false
        },
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  padding-bottom: 1rem

.header
  margin-bottom: 1.5rem

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
  margin-top: 1.5rem
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
