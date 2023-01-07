<template>
  <div>
    <div
      :class="{
        'saving-in-progress': savingClass,
        'successfully-saved': savingDoneClass,
        'failed-to-save': savingFailedClass,
        'small-height': smallHeightClass,
      }"
    >
      <slot></slot>
    </div>
    <small v-if="errors && errors.length > 0" class="text-danger">{{ errorMsg }}</small>
  </div>
</template>

<script>
export default {
  name: 'SavingAnimation',

  props: {
    saving: {
      default() {
        return false
      },
      type: Boolean,
    },
    errors: {
      type: Array,
      default: null,
    },
    height: {
      default() {
        return 'normal'
      }, // normal, small
      type: String,
    },
  },

  data() {
    return {
      savingTimeout: null,
      savingDoneTimeout: null,
    }
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
      return this.errors ? this.errors.join(' ') : ''
    },
  },

  watch: {
    saving: function (nowSaving, prevSaving) {
      // watch it
      if (!prevSaving && nowSaving) {
        this.clearSavingTimeout()
        this.savingTimeout = setTimeout(this.clearSavingTimeout, 15 * 1000)
      } else if (prevSaving && !nowSaving) {
        this.clearSavingTimeout()
        this.savingDoneTimeout = setTimeout(() => {
          clearTimeout(this.savingDoneTimeout)
          this.savingDoneTimeout = null
        }, 2 * 1000)
      }
    },
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
.saving-in-progress, .successfully-saved, .failed-to-save
  $indicatorSize: 16px

  &:before
    content: ""
    background-size: $indicatorSize $indicatorSize
    width: $indicatorSize
    height: $indicatorSize
    display: block
    position: absolute
    top: 0
    bottom: 0
    right: -#{$indicatorSize + 12px}
    margin: auto
    z-index: 9

  &.saving-in-progress
    position: relative

    &:before
      background-image: var(--url-loader)

  &.successfully-saved
    position: relative

    &:before
      background-image: url('/static/img/tick.svg')

  &.failed-to-save
    position: relative

    &:before
      background-image: url('/static/img/cross.svg')
</style>
