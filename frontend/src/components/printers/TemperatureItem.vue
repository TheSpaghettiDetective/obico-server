<template>
  <div class="temp-item" :class="{ editable }" @click="onEditClicked(tempKey, tempItem)">
    <div class="icon">
      <svg v-if="heaterIcon">
        <use :href="heaterIcon" />
      </svg>
      <i v-else class="fas fa-thermometer-empty"></i>
    </div>
    <div class="title">{{ temperatureDisplayName(tempKey) }}</div>
    <div class="value-wrapper">
      <div class="value">{{ parseFloat(tempItem.actual).toFixed(1) }} °C</div>
      <div v-if="editable" class="target">/ {{ Math.round(tempItem.target) }} °C</div>
    </div>
  </div>
</template>

<script>
import { temperatureDisplayName } from '@src/lib/utils'

export default {
  name: 'TemperatureItem',

  props: {
    tempItem: {
      type: Object,
      required: true,
    },
    tempKey: {
      type: String,
      required: true,
    },
    isPluginVersionSufficient: {
      type: Boolean,
      required: true,
    },
  },

  computed: {
    heaterIcon() {
      const key = this.tempKey.toLowerCase()
      if (key.includes('bed')) {
        return '#bed-temp'
      } else if (key.includes('tool') || key.includes('extruder')) {
        return '#extruder'
      }
      return null
    },
    editable() {
      return this.isPluginVersionSufficient && this.tempItem.target !== null
    },
  },

  methods: {
    onEditClicked(key, item) {
      if (this.editable) {
        this.$emit('TempEditClicked', key, item)
      }
    },
    temperatureDisplayName,
  },
}
</script>

<style lang="sass" scoped>
.temp-item
  display: flex
  width: 100%
  background-color: var(--color-background)
  padding: .8125rem
  border-radius: var(--border-radius-md)
  gap: 1rem
  align-items: center
  &.editable
    cursor: pointer
.icon
  width: 36px
  height: 36px
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-primary)
  color: var(--color-on-primary)
  border-radius: var(--border-radius-sm)
  svg
    width: 20px
    height: 20px
    color: var(--color-on-primary)

.value-wrapper
  margin-left: auto
  display: flex
  gap: .375rem
.value
  font-weight: bold
.target
  color: var(--color-text-secondary)
</style>
