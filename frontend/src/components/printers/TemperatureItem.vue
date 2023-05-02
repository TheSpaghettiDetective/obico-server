<template>
  <div class="temp-item" :class="{ editable: editable }" @click="onEditClicked(tempKey, tempItem)">
    <div class="icon">
      <svg>
        <use :href="tempKey.toLowerCase().includes('bed') ? '#bed-temp' : '#extruder'" />
      </svg>
    </div>
    <div class="title">{{ temperatureDisplayName(tempKey) }}</div>
    <div class="value-wrapper">
      <div class="value">{{ parseFloat(tempItem.actual).toFixed(1) }} °C</div>
      <div class="target">/ {{ Math.round(tempItem.target) }} °C</div>
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
    editable: {
      type: Boolean,
      required: true,
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
  cursor: pointer
.icon
  width: 36px
  height: 36px
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-primary)
  border-radius: var(--border-radius-sm)
  svg
    width: 20px
    height: 20px
    color: var(--color-on-primary)
.title

.value-wrapper
  margin-left: auto
  display: flex
  gap: .375rem
.value
  font-weight: bold
.target
  color: var(--color-text-secondary)
</style>
