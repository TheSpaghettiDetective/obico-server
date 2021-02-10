<template>
  <div class="wrapper">
    <div
      class="pull-to-reveal"
      :data-id="id"
      v-bind:class="{'enabled': enable}"
      ref="pullToRevealWrapper"
    >
      <slot></slot>
    </div>
    <div v-if="showEdge && status === 'closed'" class="showing-edge"></div>
    <div class="spaceholder" ref="placeholder"></div>
  </div>
</template>

<script>
export default {
  name: 'PullToReveal',

  props: {
    id: {
      type: String,
      required: true
    },
    enable: {
      default() {return true},
      type: Boolean,
    },
    maxElementHeight: {
      type: Number,
      required: true
    },
    animationTime: {
      default() {return .5},
      type: Number,
    },
    topOffsets: {
      default() {return null},
      type: Object,
    },
    zIndex: {
      default() {return 9},
      type: Number,
    },
    showEdge: {
      default() {return false},
      type: Boolean,
    },
    heightMultiplicator: {
      default() {return 2},
      type: Number,
    },
    shiftContent: {
      default() {return true},
      type: Boolean,
    },
  },

  data() {
    return {
      status: 'closed',
    }
  },

  methods: {
    toggleBlock(scrollPosition) {
      const elem = document.querySelector(`.pull-to-reveal[data-id='${this.id}']`)

      if (scrollPosition === 0) {
        // Open
        if (this.topOffsets) {
          const windowWidth = window.innerWidth

          let maxAppropriate = 0
          for (const offset in this.topOffsets) {
            if (offset !== 'default' && windowWidth <= offset && this.topOffsets[offset] > maxAppropriate) {
              maxAppropriate = this.topOffsets[offset]
            }
          }
          
          if (!maxAppropriate) {
            maxAppropriate = this.topOffsets['default']
          }

          elem.style.top = `${maxAppropriate}px`
        } else {
          elem.style.top = 0
        }

        this.status = 'opened'

        // Shift content to not cover it by revealed block
        if (this.shiftContent) {
          this.$refs.placeholder.style.height = window.getComputedStyle(this.$refs.pullToRevealWrapper).height
        }
        
      } else {
        // Hide
        elem.style.top = `${-this.maxElementHeight * this.heightMultiplicator}px`
        this.status = 'closed'

        if (this.shiftContent) {
          this.$refs.placeholder.style.height = 0
        }
      }
    }
  },

  mounted() {
    if (this.enable) {
      // Scroll down by 1px be able to scroll up right after page load
      window.onload = function() {
        if (window.scrollY === 0) {
          window.scrollBy({top: 1, behavior: 'smooth'})
        }
      }

      // Dynamic styles
      const elem = document.querySelector(`.pull-to-reveal[data-id='${this.id}']`)
      elem.style.top = `${-this.maxElementHeight * this.heightMultiplicator}px`
      elem.style.zIndex = this.zIndex
      elem.style.transition = `all ${this.animationTime}s`
      this.$refs.placeholder.style.transition = `all ${this.animationTime}s`

      // Setup handler to show on scroll up
      const handler = this.toggleBlock

      let lastKnownScrollPosition = 0
      let ticking = false

      document.addEventListener('scroll', function() {
        lastKnownScrollPosition = window.scrollY

        if (!ticking) {
          window.requestAnimationFrame(function() {
            handler(lastKnownScrollPosition)
            ticking = false
          })

          ticking = true
        }
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.pull-to-reveal.enabled
  position: fixed
  left: 0
  width: 100%

.showing-edge
  width: 100%
  height: 10px
  background-color: #4E5D6C
  position: fixed
  top: 0
  left: 0
  z-index: 2

.spaceholder
  height: 0
</style>
