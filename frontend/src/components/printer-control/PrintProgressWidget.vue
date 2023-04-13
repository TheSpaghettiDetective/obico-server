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
              <div class="info-line">
                <div class="label">
                  <div class="icon"><i class="fas fa-info"></i></div>
                  <div class="title">Status</div>
                </div>
                <div class="value">
                  <div v-if="isPrinting" :class="printer.isPaused() ? 'text-warning' : ''">
                    {{ printer.status.state.text }}
                  </div>
                  <div
                    v-else-if="!print.status.isActive"
                    class="print-status-color"
                    :class="print.status.key"
                  >
                    {{ print.status.title }}
                  </div>
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

              <div v-if="isPrinting" class="info-line">
                <div class="label">
                  <div class="icon"><i class="fas fa-clock"></i></div>
                  <div class="title">Remaining</div>
                </div>
                <div class="value">
                  <span v-if="timeRemaining">{{ timeRemaining }}</span>
                  <span v-else class="text-secondary">Calculating...</span>
                </div>
              </div>
              <div v-else class="info-line">
                <div class="label">
                  <div class="icon"><i class="fas fa-clock"></i></div>
                  <div class="title">Duration</div>
                </div>
                <div v-if="!print.status.isActive" class="value">
                  {{ print.duration || '-' }}
                </div>
                <b-spinner v-else small></b-spinner>
              </div>
            </div>

            <div v-if="isPrinting" class="progress-container">
              <div class="percentage-progress">{{ printProgressPercentage }}%</div>

              <div class="progress-bar-wrapper">
                <div class="progress-bar-inner" :style="`width: ${printProgressPercentage}%`"></div>
              </div>
              <div class="layer-progress">
                <span>{{ printProgressMillimeters }}</span>
                <span v-if="printMillimetersTotal"> / {{ printMillimetersTotal }}</span>
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
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import GCodeDetails from '@src/components/GCodeDetails.vue'
import { humanizedDuration } from '@src/lib/formatters'

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
    isPrintStarting: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      timeRemaining: null,
      printProgressPercentage: 0,
      printProgressMillimeters: 0,
      printMillimetersTotal: 0,
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

  methods: {
    updateState() {
      if (!this.isPrinting) return

      // Time remaining
      const remaining = this.printer.status?.progress?.printTimeLeft
      this.timeRemaining = Number.isInteger(remaining) ? humanizedDuration(remaining) : null

      // Progress bar
      this.printProgressPercentage = Math.round(this.printer.progressCompletion())
      this.printProgressMillimeters = Math.round(this.printer.status?.currentZ || 0)
      this.printMillimetersTotal = Math.round(
        this.printer.status?.file_metadata?.analysis?.printingArea?.maxZ || 0
      )
    },

    onRepeatClicked(ev) {
      this.$emit('PrintActionRepeatClicked', ev)
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
      opacity: .5
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
    border-radius: 999px
    background-color: var(--color-primary)
.empty-state-text
  text-align: center
  font-size: 1.125rem
</style>