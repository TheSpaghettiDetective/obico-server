<template>
  <widget-template>
    <template #title>Failure Detection</template>
    <template #content>
      <div class="wrapper">
        <help-widget
          v-if="!isWatching"
          id="not-watching-reason"
          class="help-message"
          :text-before="notWatchingExplanation"
        ></help-widget>
        <div class="header">
          <div class="dh-balance">
            <div class="label-line">Detective</div>
            <div class="label-line">Hours Balance</div>
            <div class="value-wrapper">
              <svg><use href="#svg-hour-glass" /></svg>
              <div class="value" :class="{ small: dhBadgeNum === 'Unlimited' }">
                {{ dhBadgeNum }}
              </div>
            </div>
          </div>
          <div class="gauge-wrapper">
            <failure-detection-gauge
              :normalized-p="printer.normalized_p"
              :is-watching="isWatching"
            />
          </div>
        </div>
        <div class="controls">
          <div class="line">
            <div class="label">Enable AI failure detection</div>
            <div class="switch">
              <div class="custom-control custom-switch">
                <input
                  :id="'watching_enabled-toggle-' + printer.id"
                  type="checkbox"
                  name="watching_enabled"
                  class="custom-control-input update-printer"
                  :checked="enableFailureDetection"
                  @click="onFailureDetectionToggled"
                />
                <label
                  class="custom-control-label"
                  :for="'watching_enabled-toggle-' + printer.id"
                  style="font-size: 1rem"
                ></label>
              </div>
            </div>
          </div>
          <div class="line">
            <div class="label">Pause on detected failures</div>
            <div class="switch">
              <div class="custom-control custom-switch">
                <input
                  :id="'pause_on_failure-toggle-' + printer.id"
                  type="checkbox"
                  name="pause_on_failure"
                  class="custom-control-input update-printer"
                  :checked="pauseOnFailure"
                  @click="onPauseOnFailureToggled"
                />
                <label
                  class="custom-control-label"
                  :for="'pause_on_failure-toggle-' + printer.id"
                  style="font-size: 1rem"
                ></label>
              </div>
            </div>
          </div>
        </div>
        <div v-if="printer.alertUnacknowledged()" class="failure-detected-message">
          <div class="warning-message">
            <i class="fa-solid fa-triangle-exclamation"></i>
            Failure Detected!
          </div>
          <b-button variant="outline-warning custom-button" @click="onNotAFailureClicked($event)"
            >Not a Failure?</b-button
          >
        </div>
      </div>
    </template>
  </widget-template>
</template>

<script>
import { user } from '@src/lib/page-context'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'
import HelpWidget from '@src/components/HelpWidget.vue'

export default {
  name: 'FailureDetectionWidget',

  components: {
    WidgetTemplate,
    FailureDetectionGauge,
    HelpWidget,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      user: null,
      enableFailureDetection: false,
      pauseOnFailure: false,
    }
  },

  computed: {
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return 'Unlimited'
      } else {
        return Math.round(this.user.dh_balance) + 'H'
      }
    },
    isWatching() {
      return !this.printer.not_watching_reason
    },
    notWatchingExplanation() {
      if (this.isWatching) return ''
      let reason = this.printer.not_watching_reason
      return `${reason}`
    },
  },

  created() {
    this.user = user()
    this.enableFailureDetection = this.printer.watching_enabled
    this.pauseOnFailure = this.printer.action_on_failure === 'PAUSE'
  },

  methods: {
    onFailureDetectionToggled() {
      this.enableFailureDetection = !this.enableFailureDetection
      this.$emit('updateSettings', {
        settingName: 'watching_enabled',
        settingValue: this.enableFailureDetection,
      })
    },
    onPauseOnFailureToggled() {
      this.pauseOnFailure = !this.pauseOnFailure
      this.$emit('updateSettings', {
        settingName: 'action_on_failure',
        settingValue: this.pauseOnFailure ? 'PAUSE' : 'NONE',
      })
    },
    onNotAFailureClicked(event) {
      this.$emit('notAFailureClicked', event, false)
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  padding-bottom: 1rem

.header
  display: flex
  justify-content: space-between
  align-items: center
  @media (max-width: 510px)
    flex-direction: column

.dh-balance
  .label-line
    color: var(--color-text-secondary)
    line-height: 1.3
    @media (max-width: 510px)
      text-align: center
  .value-wrapper
    margin-top: .125rem
    color: var(--color-text-primary)
    display: flex
    align-items: center
    gap: 0.25rem
    svg
      width: 1.5rem
      height: 2rem
    .value
      font-size: 1.5rem
      text-transform: uppercase
      &.small
        font-size: 1rem
        text-transform: none
        margin-top: 2px

.gauge-wrapper
  transform: scale(0.9)
  transform-origin: right
  @media (max-width: 510px)
    transform-origin: center

.controls
  margin-top: 1rem
  .line
    display: flex
    justify-content: space-between
    align-items: center
    padding: 0.5rem 0
    border-bottom: 1px solid var(--color-divider-muted)
    &:last-of-type
      border-bottom: none

.help-message
  position: absolute
  top: 8px
  right: 12px

.failure-detected-message
  margin-top: 1rem
  display: flex
  gap: 1.5rem
  align-items: center
  @media (max-width: 510px)
    flex-direction: column
    gap: 0.75rem
  .warning-message
    background-color: var(--color-warning)
    color: var(--color-on-warning)
    padding: 0.625rem 1rem
    border-radius: var(--border-radius-sm)
    flex: 1
    text-align: center
    font-weight: bold
    font-size: normal
    i
      margin-right: 0.25rem
</style>
