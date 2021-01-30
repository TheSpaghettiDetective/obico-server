<template>
  <div :class="{'saving-in-progress': savingClass, 'successfully-saved': savingDoneClass, 'small-height': smallHeightClass}">
    <slot></slot>
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
    saving: String,
    height: {
      default() {return 'normal'}, // normal, small
      type: String
    }
  },

  watch: {
    saving: function(nowSaving, prevSaving) { // watch it
      if (prevSaving !== 'saving' && nowSaving === 'saving') {
        this.savingTimeout = setTimeout(this.clearSavingTimeout, 15*1000)
      } else if (prevSaving !== 'done' && nowSaving === 'done') {
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
      return this.saving === 'saving' && this.savingTimeout
    },
    savingDoneClass() {
      return this.saving === 'done' && this.savingDoneTimeout
    },
    smallHeightClass() {
      return this.height === 'small'
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

.error-message
  margin-bottom: 10px
</style>
