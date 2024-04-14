<template>
  <div class="obico-gauge-container">
    <span id="title" :style="{ color: titleColor }">{{ titleText }}</span>
    <div class="obico-gauge">
      <radial-gauge :value="value" :options="computedOptions"></radial-gauge>
    </div>
    <hr />
  </div>
</template>

<script>
import RadialGauge from 'vue2-canvas-gauges/src/RadialGauge'
import { Themes } from '@static/js/color-scheme'
import { currentThemeValue } from '@src/lib/color-scheme-controller'

export default {
  name: 'FailureDetectionGauge',
  components: {
    RadialGauge,
  },
  props: {
    normalizedP: {
      type: Number,
      required: true,
    },

    isWatching: {
      type: Boolean,
      default: true,
    },

    options: {
      // https://canvas-gauges.com/documentation/user-guide/configuration
      type: Object,
      default: null,
    },
  },

  computed: {
    computedOptions() {
      if (this.options !== null) {
        return this.options
      }

      const inactiveColor = {
        highlight1: currentThemeValue() === Themes.Light ? '#929292' : '#8395a7',
        highlight2: currentThemeValue() === Themes.Light ? '#b7b7b7' : '#a8bacc',
        highlight3: currentThemeValue() === Themes.Light ? '#7b7b7b' : '#6c7e90',
        needle: currentThemeValue() === Themes.Light ? '#2d3e4f' : '#ffffff',
      }

      return {
        valueDec: 0,
        valueInt: 0,
        width: 240,
        height: 240,
        units: false,
        box: false,
        minValue: 0,
        maxValue: 100,
        majorTicks: ['', '', '', ''],
        minorTicks: 4,
        highlights: [
          { from: 0, to: 33, color: this.isWatching ? '#5cb85c' : inactiveColor.highlight1 },
          { from: 33, to: 67, color: this.isWatching ? '#f0ad4e' : inactiveColor.highlight2 },
          { from: 67, to: 100, color: this.isWatching ? '#d9534f' : inactiveColor.highlight3 },
        ],
        colorPlate: 'rgba(255,255,255,.0)',
        colorTitle: '#5cb85c',
        colorStrokeTicks: '#EBEBEB',
        colorNeedleEnd: this.isWatching ? 'rgba(255, 160, 122, .9)' : inactiveColor.needle,
        colorNeedle: this.isWatching ? 'rgba(240, 128, 128, 1)' : inactiveColor.needle,
        colorNeedleShadowUp: this.isWatching ? 'rgba(2,255,255,0.2)' : inactiveColor.needle,
        valueBox: false,
        animationRule: 'bounce',
        animationDuration: 500,
        animatedValue: true,
        startAngle: 90,
        ticksAngle: 180,
        borders: false,
      }
    },
    value() {
      return this.normalizedP * 100
    },
    titleText() {
      if (!this.isWatching) {
        return `${this.$i18next.t('Not Watching')}`
      }
      switch (this.level()) {
        case 0:
          return `${this.$i18next.t('Looking Good')}`
        case 1:
          return `${this.$i18next.t('Fishy...')}`
        case 2:
          return `${this.$i18next.t('Failing!')}`
        default:
          return `${this.$i18next.t("Looking Good")}`
      }
    },
    titleColor() {
      if (!this.isWatching) {
        return 'var(--color-text-secondary)'
      }
      switch (this.level()) {
        case 0:
          return '#5cb85c'
        case 1:
          return '#f0ad4e'
        case 2:
          return '#d9534f'
        default:
          return '#5cb85c'
      }
    },
  },

  methods: {
    level() {
      if (this.value > 66) {
        return 2
      } else if (this.value > 33) {
        return 1
      } else {
        return 0
      }
    },
  },
}
</script>

<style lang="sass" scoped>
#title
  position: absolute
  left: 0px
  text-align: center
  width: 100%
  top: 50%

.obico-gauge-container
  position: relative
  padding: 0 16px
  .obico-gauge
    text-align: center
    padding: 8px
    margin-bottom: -150px
    pointer-events: none
  hr
    background-color: #EBEBEB
    height: 1px
    margin-top: 15px
</style>
