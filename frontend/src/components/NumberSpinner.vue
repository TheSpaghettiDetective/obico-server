<template>
  <div :class="'input-group ' + groupClass">
    <div class="input-group-prepend">
      <button
        type="button"
        :style="{ 'min-width': buttonsWidth }"
        :class="'btn btn-num-spinner ' + buttonsClass"
        @click="decrease"
        @mousedown="whileMouseDown(decrease)"
        @mouseup="clearTimer"
      >
        <slot name="decrementButton">
          <strong>-</strong>
        </slot>
      </button>
    </div>

    <input
      type="text"
      :class="classes"
      :style="{ 'text-align': textAlign }"
      :min="min"
      :max="max"
      :step="step"
      :value="value"
      pattern="\d+"
      @input="onInput"
      @paste="onInput"
      @change="onInput"
      @focusout="onInput"
    />

    <div class="input-group-append">
      <button
        type="button"
        :style="{ 'min-width': buttonsWidth }"
        :class="'btn btn-num-spinner ' + buttonsClass"
        @click="increase"
        @mousedown="whileMouseDown(increase)"
        @mouseup="clearTimer"
      >
        <slot name="incrementButton">
          <strong>+</strong>
        </slot>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NumberSpinner',
  props: {
    min: {
      type: Number,
      default: () => null,
    },
    max: {
      type: Number,
      default: () => null,
    },
    step: {
      type: Number,
      default: () => null,
    },
    value: {
      type: Number,
      required: true,
    },
    groupClass: {
      type: String,
      default: () => '',
    },
    buttonsClass: {
      type: String,
      default: () => '',
    },
    buttonsWidth: {
      type: String,
      default: () => '2.5rem',
    },
    textAlign: {
      type: String,
      default: () => 'center',
    },
    mouseDownSpeed: {
      default: () => 500,
      type: Number,
    },
  },
  computed: {
    classes() {
      return 'form-control'
    },
  },
  created() {
    this.timer = null
  },
  methods: {
    increase() {
      if (this.max === null || this.max > this.value) {
        this.onNewValue(Math.min(this.max, this.value + 1))
      }
    },
    decrease() {
      if (this.min === null || this.min < this.value) {
        this.onNewValue(Math.max(this.min, this.value - this.step))
      }
    },
    onInput(event) {
      this.onNewValue(event.target.value)
    },
    onNewValue(value) {
      const v = parseFloat(value)
      if (v) {
        if (this.min === null || (v >= this.min && (this.max === null || v <= this.max))) {
          this.$emit('input', v)
        }
      }
    },
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    whileMouseDown(callback) {
      if (this.timer === null) {
        this.timer = setInterval(() => {
          callback()
        }, this.mouseDownSpeed)
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.btn-num-spinner
  outline: none
  box-shadow: none
</style>
