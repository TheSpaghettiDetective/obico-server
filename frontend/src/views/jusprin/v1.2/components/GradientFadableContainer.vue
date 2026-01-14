<template>
  <div
    ref="container"
    class="gradient-fade-wrapper"
    :class="{ 'is-unfaded': isUnfaded }"
    @click="toggleFade"
  >
    <slot></slot>
    <div v-if="hasFade && !isUnfaded" class="fade-overlay"></div>
  </div>
</template>

<script>
export default {
  name: 'GradientFadableContainer',
  data() {
    return {
      isUnfaded: false,
      hasFade: false,
    }
  },
  mounted() {
    this.checkIfNeedsFade()
  },
  updated() {
    this.checkIfNeedsFade()
  },
  methods: {
    toggleFade() {
      this.isUnfaded = !this.isUnfaded

      // Wait for transition to complete before rechecking
      setTimeout(() => {
        this.checkIfNeedsFade()
      }, 300)
    },
    checkIfNeedsFade() {
      this.$nextTick(() => {
        const el = this.$refs.container
        if (!this.isUnfaded) {
          this.hasFade = el.scrollHeight > el.clientHeight
        } else {
          this.hasFade = false
        }
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.gradient-fade-wrapper
  position: relative
  max-height: 8rem
  overflow: hidden
  transition: max-height 0.3s ease-out
  cursor: pointer

  &.is-unfaded
    max-height: 1000px

.fade-overlay
  position: absolute
  bottom: 0
  left: 0
  right: 0
  height: 3rem
  background: linear-gradient(transparent, var(--message-bg, white))
  pointer-events: none
</style>
