<template>
  <widget-template>
    <template #title>{{ $t("Failure Detection") }}</template>
    <template #content>
      <div class="wrapper">
        <div v-if="isEnt" class="dh-balance-wrapper">
          <a
            href="/user_preferences/dh/"
            class="btn shadow-none action-btn icon-btn hours-btn"
            :style="{ marginRight: `${String(dhBadgeNum).length * 0.25}rem` }"
            :title="dhBadgeNum + ' '+$t('AI Detection Hours')"
          >
            <svg class="custom-svg-icon">
              <use href="#svg-hour-glass"></use>
            </svg>
            <span id="user-credits" class="badge badge-light">{{ dhBadgeNum }}</span>
            <span class="sr-only">{{ $t("AI Detection Hours") }}</span>
          </a>
        </div>
        <div class="header">
          <div class="gauge-wrapper">
            <failure-detection-gauge
              :normalized-p="printer.normalized_p"
              :is-watching="isWatching"
            />
          </div>
          <div v-if="printer.not_watching_reason" class="overlay-info">
            <muted-alert class="muted-alert">
              <span
                >{{$t("Not watching")}} ({{ printer.not_watching_reason }}).
                <a
                  :href="getDocUrl('/user-guides/detective-not-watching/')"
                  target="_blank"
                  >{{$t("Learn all possible reasons")}}
                  <small><i class="fas fa-external-link-alt"></i></small></a
              ></span>
            </muted-alert>
          </div>
        </div>
        <div class="controls">
          <div class="line">
            <label class="label" :for="'watching_enabled-toggle-' + printer.id">
              {{$t("Enable AI failure detection")}}
              <div v-if="!enableFailureDetection" class="text-muted">
                {{$t("AI failure detection is disabled. You are on your own.")}}
              </div>
            </label>
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
            <label class="label" :for="'pause_on_failure-toggle-' + printer.id">
              {{ $t("Pause on detected failures") }}
              <div v-if="!pauseOnFailure" class="text-muted">
                {{$t("You will still be alerted via notifications.")}}
              </div>
            </label>
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
            <i class="fas fa-exclamation-triangle"></i>
            {{$t("Failure Detected!")}}
          </div>
          <b-button variant="outline-warning custom-button" @click="onNotAFailureClicked($event)"
            >{{ $t("Not a Failure?") }}</b-button
          >
        </div>
      </div>
    </template>
  </widget-template>
</template>

<script>
import { user, settings } from '@src/lib/page-context'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'
import MutedAlert from '@src/components/MutedAlert.vue'

export default {
  name: 'FailureDetectionWidget',

  components: {
    WidgetTemplate,
    FailureDetectionGauge,
    MutedAlert,
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
      isEnt: false,
    }
  },

  computed: {
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return 'Unlimited'
      } else {
        return Math.round(this.user.dh_balance)
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
    const { IS_ENT } = settings()
    this.isEnt = !!IS_ENT
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
  position: relative
  display: flex
  justify-content: center
  align-items: center
  @media (max-width: 510px)
    flex-direction: column

  .overlay-info
    position: absolute
    left: 0
    bottom: 0
    right: 0
    top: 0
    display: flex
    align-items: center
    justify-content: center
    .muted-alert
      position: relative
      z-index: 2
    &::before
      content: ''
      position: absolute
      left: 0
      bottom: 0
      right: 0
      top: 0
      background: var(--color-surface-secondary)
      z-index: 1
      opacity: 0.97

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
    .label
      margin-bottom: 0
      font-size: 1rem
      .text-muted
        font-size: 0.875rem

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

.dh-balance-wrapper
  position: absolute
  top: 8px
  right: 12px
.btn.hours-btn
  padding-left: 0
  padding-right: 0
  width: 36px
  position: relative
  color: var(--color-text-primary)
  .badge
    position: absolute
    left: 18px
    top: 4px
    border-radius: var(--border-radius-sm)
    background-color: var(--color-primary)
    height: auto
    font-size: .625rem
.custom-svg-icon
  height: 1.3rem
  width: 1.3rem
</style>
