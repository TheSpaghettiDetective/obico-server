<template>
  <div class="input-group input-group-sm input-wrapper">
    <div class="input-group-prepend">
      <button
        class="btn btn-outline-secondary control-button"
        type="button"
        :disabled="disable"
        @click="
          inputValue = inputValue > 0 ? Math.round((inputValue - step) * 10) / 10 : 0
          $emit('input', inputValue)
        "
      >
        ↓
      </button>
    </div>
    <input
      type="text"
      class="form-control text-center field_required"
      disabled
      aria-describedby="basic-addon1"
      :value="inputValue + ' ' + unit"
      :style="{ opacity: disable ? 0.3 : 1 }"
    />
    <div class="input-group-append">
      <button
        class="btn btn-outline-secondary control-button"
        type="button"
        :disabled="disable"
        @click="
          inputValue = Math.round((inputValue + step) * 10) / 10
          $emit('input', inputValue)
        "
      >
        ↑
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NumberInput',

  props: {
    value: {
      type: Number,
      default: 0,
    },
    step: {
      type: Number,
      default: 0.5,
    },
    disable: {
      type: Boolean,
      default: false,
    },
    unit: {
      type: String,
      default: 'mm',
    },
  },

  data() {
    return {
      inputValue: this.value,
    }
  },

  watch: {
    value(newValue) {
      this.inputValue = newValue
    },
  },
}
</script>

<style lang="sass" scoped>
.input-group.input-wrapper
  border-radius: var(--border-radius-sm)
  overflow: hidden
  border: 1px solid var(--color-divider)

  .control-button
    border: none

  .btn-outline-secondary
    background-color: var(--color-input-background)

    &:hover, &:focus, &:active
      color: var(--color-text-primary)
      background-color: var(--color-input-background)
      opacity: .8
      outline: none
      box-shadow: none !important
      border: none


  input.form-control
    background-color: var(--color-input-background)
    color: var(--color-text-primary)
    width: 6rem
    border: none
    border-left: 2px solid var(--color-divider)
    border-right: 2px solid var(--color-divider)
</style>
