<template>
  <div class="wrapper">
    <div class="pull-to-reveal" ref="pullToRevealWrapper">
      <slot></slot>
    </div>
    <div v-show="showEdge" class="showing-edge" ref="showingEdge"></div>
    <div class="spaceholder" ref="spaceholder"></div>
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
  },

  data() {
    return {
      status: 'closed',
      animationTime: .5,
    }
  },

  mounted() {
    const elem = this.$refs.pullToRevealWrapper
    const spaceholder = this.$refs.spaceholder
    // const showingEdge = this.$refs.showingEdge
    const animationTime = this.animationTime

    elem.style.transition = `all ${animationTime}s`
    spaceholder.style.transition = `all ${animationTime}s`

    window.onload = function() {
      // Scroll down by 1px be able to scroll up right after page load
      if (window.scrollY === 0) {
        window.scrollBy({top: 1, behavior: 'smooth'})
      }

      const elemHeight = parseInt(window.getComputedStyle(elem).height)
      elem.style.top = `-${elemHeight * 2}px`
    }
  },

  created() {
    window.addEventListener('scroll', this.handleScroll)
    document.querySelector('body').style.minHeight = '101vh'
  },

  destroyed() {
    window.removeEventListener('scroll', this.handleScroll)
    document.querySelector('body').style.minHeight = ''
  },

  methods: {
    handleScroll() {
      const scrollPosition = window.pageYOffset
      const elem = this.$refs.pullToRevealWrapper
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
          this.$refs.spaceholder.style.height = `${elemHeight}px`
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
          this.$refs.spaceholder.style.height = 0
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
    z-index: 1
    top: -9999px

  .showing-edge
    width: 100%
    height: 10px
    background-color: #4E5D6C
    position: absolute
    top: 0
    left: 0
    z-index: -1

  .spaceholder
    height: 0
</style>
