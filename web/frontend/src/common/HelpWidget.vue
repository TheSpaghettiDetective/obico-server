<template>
  <div class="help-wrapper" v-click-outside="() => show = false">

    <!-- Slot for text -->
    <div class="text" @click="positionWidget(); show = !show;">
      <slot></slot>
    </div>

    <div class="widget-wrapper" ref="widgetWrapper">

      <!-- Help icon -->
      <div class="question-mark" @click="positionWidget(); show = !show;">
        <svg viewBox="0 0 40 40" fill="currentColor">
          <use href="#svg-question-icon" />
        </svg>
      </div>

      <!-- Help widget -->
      <transition name="pop-up">
        <div v-show="show" class="widget" :class="[xDirection, yDirection]">
          <div class="header">
            <div class="title">
              <i class="fas fa-question-circle"></i>
              In case you were wondering...
            </div>
            <div class="close-button" @click="show = false">
              <svg viewBox="0 0 16 16" fill="currentColor">
                <use href="#svg-cross-icon" />
              </svg>
            </div>
          </div>

          <!-- Help content -->
          <div class="content">

            <!-- basic-streaming-on-pricing-page -->
            <template v-if="id === 'basic-streaming-on-pricing-page'">
              <p>Basic Streaming is at 0.1fps (1 frame per 10 seconds).</p>
              <p>The stream is on only when the printer is printing.</p>
              <strong>
                Learn more about
                <a href="https://www.thespaghettidetective.com/docs/webcam-streaming-for-human-eyes/" target="_blank" class="external">the differences between the Premium Streaming and the Basic Streaming</a>
              </strong>
            </template>

            <!-- detective-hours-free-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-free-plan-on-pricing-page'">
              <h3>Yup! Even Free account gets 10 Detective Hours for FREE each month.</h3>
              <ul>
                <li>Unused Detective Hours roll over month to month.</li>
                <li>You can also <a href="https://www.thespaghettidetective.com/docs/how-does-credits-work/">earn free Detective Hours by helping her improve</a>.</li>
              </ul>
              <p>
                Learn more about
                <strong>
                  <a href="https://www.thespaghettidetective.com/docs/how-does-detective-hour-work/" target="_blank" class="external">how the Detective Hour works</a>
                </strong>
              </p>
            </template>

            <!-- detective-hours-pro-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-pro-plan-on-pricing-page'">
              <h3>Pro plan includes 50 Detective Hours each month.</h3>
              <ul>
                <li>Unused Detective Hours roll over month to month.</li>
                <li>Detective Hours expire when subscription ends.</li>
                <li>You can also <a href="https://www.thespaghettidetective.com/docs/how-does-credits-work/">earn more Detective Hours by helping her improve</a>.</li>
              </ul>
              <p>
                Learn more about
                <strong>
                  <a href="https://www.thespaghettidetective.com/docs/how-does-detective-hour-work/" target="_blank" class="external">how the Detective Hour works</a>
                </strong>
              </p>
            </template>

            <!-- premium-streaming-on-pricing-page -->
            <template v-if="id === 'premium-streaming-on-pricing-page'">
              <div class="video-wrapper">
                <iframe src="https://www.youtube.com/embed/liBTaFjkBnU" frameborder="0" allowfullscreen width="100%"></iframe>
              </div>
              <h3>Webcam streaming at 25fps (25 frames per second).</h3>
              <h3>It is always on regardless if your printer is printing.</h3>
              <p>
                Learn more about
                <strong>
                  <a href="https://www.thespaghettidetective.com/docs/webcam-streaming-for-human-eyes/" target="_blank" class="external">the differences between the Premium Streaming and the Basic Streaming</a>
                </strong>
              </p>
            </template>

            <!-- tunneling-free-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-free-plan-on-pricing-page'">
              <p>Securely tunnel to your OctoPrint from anywhere.</p>
              <p>Free plan is subject to 50MB/month data cap.</p>
              <p>
                Learn more about
                <strong>
                  <a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/" target="_blank" class="external">OctoPrint Tunneling</a>
                </strong>
              </p>
            </template>

            <!-- tunneling-pro-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-pro-plan-on-pricing-page'">
              <h3>Securely tunnel to your OctoPrint from anywhere. Unlimited.</h3>
              <p>
                Learn more about
                <strong>
                  <a href="https://www.thespaghettidetective.com/docs/octoprint-tunneling/" target="_blank" class="external">OctoPrint Tunneling</a>
                </strong>
              </p>
            </template>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
/**
 * Pop-up widget to show additional help notes
 * To work properly should wrap raw text
 *
 * @example
 * <div>
 *   <help-widget src="...">Webcam streaming</help-widget>
 * </div>
 */

import ClickOutside from 'vue-click-outside'

export default {
  name: 'HelpWidget',

  data() {
    return {
      show: false,
      xDirection: 'left',
      yDirection: 'top',
    }
  },

  directives: {
    ClickOutside,
  },

  props: {
    id: {
      type: String,
      required: true
    },
  },

  methods: {
    // Find preferred direction for widget to pup-up
    // Based on help icon position inside viewport
    positionWidget() {
      const widgetWidth = 360 // should be synced with `$widget-width` in styles
      // const widgetHeight = 360 // should be synced with `$widget-height` in styles
      const minHorizontalSpace = widgetWidth + 10
      // const minVerticalSpace = widgetHeight + 10

      const helpIconPosition = this.$refs.widgetWrapper.getBoundingClientRect()

      const distanceFromRightEdge = window.innerWidth - (helpIconPosition.left + helpIconPosition.width)
      // const distanceFromBottomEdge = window.innerHeight - (helpIconPosition.top + helpIconPosition.height)

      if (distanceFromRightEdge < minHorizontalSpace) {
        this.xDirection = 'right'
      } else {
        this.xDirection = 'left'
      }

      // if (distanceFromBottomEdge < minVerticalSpace) {
      //   this.yDirection = 'bottom'
      // } else {
      //   this.yDirection = 'top'
      // }
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.help-wrapper
  display: inline
  position: relative
  text-decoration: underline
  text-decoration-color: rgb(var(--color-text-help))
  .text
    display: inline
    &:hover
      cursor: pointer

.widget-wrapper
  $widget-width: 360px
  $widget-header-height: 40px
  $x-breakpoint: #{$widget-width + 20px}
  $x-breakpoint-2: #{$widget-width * 2 + 20px}
  position: relative
  left: .1rem
  width: 1rem
  height: 1rem
  display: inline-block

  .question-mark
    display: flex
    color: rgb(var(--color-text-help))
    transition: all .2s ease-out
    height: 1rem
    &:hover
      cursor: pointer

    svg
      width: 1rem
      height: 1rem

  .widget
    width: $widget-width
    padding-top: $widget-header-height
    z-index: 10
    position: absolute
    box-shadow: var(--shadow-widget)
    border-radius: 12px
    overflow: hidden
    background-color: #fff
    display: flex
    flex-direction: column

    @media (min-width: $x-breakpoint-2)
      &.left
        left: 100%
      &.right
        right: 100%
      &.bottom
        bottom: 100%
      &.top
        top: 100%

    @media (max-width: $x-breakpoint-2)
      left: 0rem
      right: 0rem
      top: 5rem
      margin: auto
      position: fixed

    @media (max-width: $x-breakpoint)
      left: 1rem
      right: 1rem
      width: auto

    .header
      color: #28303A
      height: $widget-header-height
      width: 100%
      display: flex
      align-items: center
      border-bottom: 1px solid #D4DAE0
      position: absolute
      top: 0
      left: 0
      width: 100%
      z-index: 10

      .title
        flex: 1
        font-size: 16px
        font-weight: 400
        padding-left: .875rem

        i
          margin-right: .125rem

      .close-button
        height: $widget-header-height
        flex: 0 0 $widget-header-height
        display: flex
        align-items: center
        justify-content: center
        color: #9CA3AF
        transition: all .2s ease-out
        &:hover
          color: #6B7280
          cursor: pointer

        svg
          width: #{$widget-header-height * .58}
          height: #{$widget-header-height * .58}

    .content
      padding: 1rem .875rem
      color: #000
      font-size: 14px
      font-weight: normal

      & > *
        margin-bottom: 1em
        display: block

      h1, h2, h3
        font-weight: bold

      h1
        font-size: 1.3em
      h2
        font-size: 1.2em
      h3
        font-size: 1.1em

      ul
        padding-left: 2em

      .video-wrapper
        position: relative
        padding-bottom: 56.25%
        height: 0

        iframe
          position: absolute
          top: 0
          left: 0
          width: 100%
          height: 100%

      a.external:after
        content: url('/static/img/link.svg')
        display: inline-block
        width: 1em
        margin-left: .25em
        position: relative
        top: .125em
</style>

<style scoped>
/*
  Widget animation
  Defined with native CSS due to SASS and Vue conflict
*/

.pop-up-enter-active {
  transition: all 0.1s ease-out;
}

.pop-up-leave-active {
  transition: all 0.1s ease-in;
}

.pop-up-enter, .pop-up-leave-to {
  transform: translate(-2rem, -1rem) scale(.8);
  opacity: 0
}
</style>
