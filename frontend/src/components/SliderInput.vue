<template>
  <div class="slidecontainer">
    <input
      type="range"
      :min="min"
      :max="max"
      :step="step"
      :value="value"
      class="slider"
      @change="$emit('change', Number($event.target.value))"
      @input="$emit('input', Number($event.target.value))"
    />
  </div>
</template>

<script>
export default {
  name: 'SliderInput',

  props: {
    value: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    min: {
      type: Number,
      default: 0,
    },
    step: {
      type: Number,
      default: 1,
    },
  },

  computed: {},
  methods: {},
}
</script>

<style lang="sass" scoped>
.slidecontainer
  width: 100%

.slider
  -webkit-appearance: none
  appearance: none
  width: 100%
  height: 5px
  background: var(--color-input-background)
  outline: none
  border: none

// The slider handle (use -webkit- (Chrome, Opera, Safari, Edge) and -moz- (Firefox) to override default look) */
.slider::-webkit-slider-thumb
  -webkit-appearance: none
  appearance: none
  width: 25px
  height: 25px
  border-radius: 50%
  background: var(--color-text-primary)
  cursor: pointer
  border: none

.slider::-moz-range-thumb
  width: 25px
  height: 25px
  border-radius: 50%
  background: var(--color-text-primary)
  cursor: pointer
  border: none
</style>
