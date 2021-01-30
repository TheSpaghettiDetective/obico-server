<template>
  <div :class="{'saving-in-progress': savingClass, 'successfully-saved': savingDoneClass, 'failed-to-save': savingFailedClass, 'small-height': smallHeightClass}">
    <slot></slot>
    <small v-if="errors && errors.length > 0" class="text-danger">{{errorMsg}}</small>
  </div>
</template>

<script>
export default {
  name: 'SavingAnimation',

  data() {
    return {
      savingTimeout: null,
      savingDoneTimeout: null,
    }
  },

  props: {
    saving: {
      default() {return false},
      type: Boolean,
    },
    errors: {
      type: Array,
    },
    height: {
      default() {return 'normal'}, // normal, small
      type: String
    }
  },

  watch: {
    saving: function(nowSaving, prevSaving) { // watch it
      if (!prevSaving && nowSaving) {
        this.clearSavingTimeout()
        this.savingTimeout = setTimeout(this.clearSavingTimeout, 15*1000)
      } else if (prevSaving && !nowSaving) {
        this.clearSavingTimeout()
        this.savingDoneTimeout = setTimeout(() => {
          clearTimeout(this.savingDoneTimeout)
          this.savingDoneTimeout = null
        }, 2*1000)
      }
    },
  },

  computed: {
    savingClass() {
      return this.saving && this.savingTimeout
    },
    savingDoneClass() {
      return !this.saving && this.savingDoneTimeout && !this.errors
    },
    savingFailedClass() {
      return !this.saving && this.savingDoneTimeout && this.errors && this.errors.length > 0
    },
    smallHeightClass() {
      return this.height === 'small'
    },
    errorMsg() {
      return this.errors.join(' ')
    }
  },

  methods: {
    clearSavingTimeout() {
      if (this.savingTimeout) {
        clearTimeout(this.savingTimeout)
        this.savingTimeout = null
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.saving-in-progress, .successfully-saved
  $indicatorSize: 16px

  &:before
    content: ""
    background-size: $indicatorSize $indicatorSize
    width: $indicatorSize
    height: $indicatorSize
    display: block
    position: absolute
    top: 10px
    right: -#{$indicatorSize + 16px}
    margin: auto
    z-index: 9


  &.small-height:before
    top: 4px

  &.saving-in-progress
    position: relative

    &:before
      background-image: url('/static/img/tail-spin.svg')

  &.successfully-saved
    position: relative

    &:before
      background-image: url('/static/img/tick.svg')

  &.failed-to-save
    position: relative

    &:before
      background-image: url('/static/img/tick.svg')
</style>
