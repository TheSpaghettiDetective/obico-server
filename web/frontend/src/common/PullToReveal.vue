<template>
  <div class="wrapper" ref="pullToRevealWrapper">
    <div>
      <div class="pull-to-reveal">
        <slot v-if="enable"></slot>
      </div>
      <div v-show="showEdge" class="showing-edge"></div>
      <div class="spaceholder"></div>
    </div>
    <div ref="staticWrapper">
      <slot v-if="!enable"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PullToReveal',

  props: {
    showEdge: {
      default() {return false},
      type: Boolean,
    },
    shiftContent: {
      default() {return true},
      type: Boolean,
    },
    enable: {
      default() {return false},
      type: Boolean,
    },
  },

  data() {
    return {
      status: 'closed',
      animationTime: .5,
    }
  },

  watch: {
    enable(enabled) {
      if(enabled) {
        this.destroyDisabled()
        this.initEnabled()
      } else {
        this.destroyEnabled()
        this.initDisabled()
      }
    }
  },

  mounted() {
    if (this.enable) {
      this.initEnabled()
    } else {
      this.initDisabled()
    }
  },

  destroyed() {
    if (this.enable) {
      this.destroyEnabled()
    } else {
      this.destroyDisabled()
    }
  },

  methods: {
    initEnabled() {
      window.addEventListener('scroll', this.handleScroll)
      document.querySelector('body').style.minHeight = '101vh'

      const elem = this.$refs.pullToRevealWrapper.querySelector('.pull-to-reveal')
      const spaceholder = this.$refs.pullToRevealWrapper.querySelector('.spaceholder')
      // const showingEdge = this.$refs.pullToRevealWrapper.querySelector('.showing-edge')
      const animationTime = this.animationTime

      elem.style.transition = `all ${animationTime}s`
      spaceholder.style.transition = `all ${animationTime}s`

      // Scroll down by 1px be able to scroll up right after page load
      if (window.scrollY === 0) {
        window.scrollBy({top: 1, behavior: 'smooth'})
      }

      window.onload = function() {
        const elemHeight = parseInt(window.getComputedStyle(elem).height)
        elem.style.top = `-${elemHeight * 2}px`
      }
    },

    destroyEnabled() {
      if (window) {
        window.removeEventListener('scroll', this.handleScroll)
      }

      if (document) {
        document.querySelector('body').style.minHeight = ''
      }

      if (this.$refs.pullToRevealWrapper) {
        const elem = this.$refs.pullToRevealWrapper.querySelector('.pull-to-reveal')
        elem.style.transition = 'none'
        elem.style.top = '-999px'

        const spaceholder = this.$refs.pullToRevealWrapper.querySelector('.spaceholder')
        spaceholder.style.transition = 'none'
      }
    },

    initDisabled() {
      const showingEdge = this.$refs.pullToRevealWrapper.querySelector('.showing-edge')

      showingEdge.style.display = 'none'

      const staticWrapper = this.$refs.staticWrapper
      staticWrapper.style.position = 'absolute'
      staticWrapper.style.width = '100%'
      staticWrapper.style.top = '0'
      staticWrapper.style.left = '0'
      staticWrapper.style.zIndex = '10'

      // const elemHeight = parseInt(window.getComputedStyle(staticWrapper).height)
      document.querySelector('body').style.paddingTop = '56px'

      window.onload = function() {
        const elemHeight = parseInt(window.getComputedStyle(staticWrapper).height)
        document.querySelector('body').style.paddingTop = `${elemHeight}px`
      }
    },

    destroyDisabled() {
      const showingEdge = this.$refs.pullToRevealWrapper
      if (showingEdge) {
        showingEdge.querySelector('.showing-edge').style.display = 'block'
      }

      const staticWrapper = this.$refs.staticWrapper
      if (staticWrapper) {
        staticWrapper.style.display = 'none'
      }

      if (document) {
        document.querySelector('body').style.paddingTop = 0
      }
    },

    handleScroll() {
      const scrollPosition = window.pageYOffset
      const elem = this.$refs.pullToRevealWrapper.querySelector('.pull-to-reveal')
      const elemHeight = parseInt(window.getComputedStyle(elem).height)

      if (scrollPosition === 0) {
        // Open

        if (this.status === 'opened') {
          return
        }

        elem.style.top = 0
        this.status = 'opened'

        // Shift content to not cover it by revealed block
        if (this.shiftContent) {
          this.$refs.pullToRevealWrapper.querySelector('.spaceholder').style.height = `${elemHeight}px`
        }

      } else {
        // Hide

        if (this.status === 'closed') {
          return
        }

        this.$emit('hide')

        elem.style.top = `-${elemHeight * 2}px`
        this.status = 'closed'

        if (this.shiftContent) {
          this.$refs.pullToRevealWrapper.querySelector('.spaceholder').style.height = 0
        }
      }
    }
  }
}
</script>

<style lang="sass" scoped>
  @use "~main/theme"

  .pull-to-reveal
    position: fixed
    left: 0
    width: 100%
    z-index: 10
    top: -9999px

  .showing-edge
    width: 100%
    height: 10px
    background-color: rgb(var(--color-surface-secondary))
    position: absolute
    top: 0
    left: 0
    z-index: -1

  .spaceholder
    height: 0
</style>
