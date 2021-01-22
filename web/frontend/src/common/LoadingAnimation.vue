/**
 * Module provides methods to give user a feedback about what is going on -
 * is data is pending, or successfully saved
 *
 * How to use:
 * 1. Import the module and add it to mixins list (see PrinterSettingsPage.vue for reference)
 * 2. Call savingInProgressFeedback(elem) before API call
 * 3. Call successfullySavedFeedback(elem) after API call in case of success
 * 4. Call clearSavingLoader(elem) after API call in case of error (to clear loading animation)
 */
<template>
  <div :class="'input-group ' + groupClass">
    <div class="input-group-prepend">
      <button
        type="button"
        :style="{'min-width': buttonsWidth}"
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
      :style="{'text-align': textAlign}"
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
        :style="{'min-width': buttonsWidth}"
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
  name: 'LoadingAnimation',

  data() {
    return {
      loading: false,
      succeeded: false,
    }
  },

  methods: {
    /**
     * Show indicator that data is saving
     * @param {Element} elem HTML element
     */
    savingInProgressFeedback: function(elem) {
      elem.classList.add('saving-in-progress')
    },

    /**
     * Show indicator that data is successfully saved
     * @param {Element} elem HTML element
     */
    successfullySavedFeedback: function(elem) {
      this.clearSavingLoader(elem)
      elem.classList.add('successfully-saved')
      setTimeout(
        () => elem.classList.remove('successfully-saved'),
        2000
      )
    },

    /**
     * Clear loading indicator (for example, in case of error)
     * @param {Element} elem HTML element
     */
    clearSavingLoader: function(elem) {
      elem.classList.remove('saving-in-progress')
    }
  },
}
</script>

<style lang="sass" scoped>
.btn-num-spinner
  outline: none
  box-shadow: none
</style>
