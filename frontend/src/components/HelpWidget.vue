<template>
  <div class="help-wrapper" v-click-outside="() => show = false">

    <!-- Slot for text -->
    <div class="text" @click="positionWidget(); show = !show;">
      <slot></slot>
    </div>

    <div class="widget-wrapper" ref="widgetWrapper">

      <!-- Help icon -->
      <div class="question-mark" @click="positionWidget(); show = !show;">
        <svg>
          <use href="#svg-question-icon" />
        </svg>
      </div>

      <!-- Help widget -->
      <transition name="pop-up">
        <div v-show="show" class="widget" :class="[xDirection, yDirection]">
            <div class="close-button" @click="show = false">
              <svg width="16" height="16">
                <use href="#svg-cross-icon" />
              </svg>
            </div>

          <!-- Help content -->
          <div class="content">

            <!-- basic-streaming-on-pricing-page -->
            <template v-if="id === 'basic-streaming-on-pricing-page'">
              <div>
                Basic Streaming:
                <ul>
                <li>Up to 5 FPS (frame-per-second)</li>
                <li>Throttled for 30 seconds every minute</li>
                </ul>
              </div>
              <div>
                Learn more about
                <a href="https://www.obico.io/docs/user-guides/webcam-streaming-for-human-eyes/" target="_blank">the differences between the Premium Streaming and the Basic Streaming <i class="fas fa-external-link-alt"></i></a>
              </div>
            </template>

            <!-- detective-hours-free-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-free-plan-on-pricing-page'">
              <h3>Yup! Even Free account gets 10 AI Detection Hours for FREE each month.</h3>
              <ul>
                <li>Unused AI Detection Hours roll over month to month.</li>
                <li>You can <a href="https://www.obico.io/docs/user-guides/how-does-credits-work/">earn free AI Detection Hours by helping her improve</a>.</li>
                <li>You can also <a class="link" href="#need-more">purchase additional AI hours</a>.</li>
              </ul>
              <p>
                Learn more about
                  <a href="https://www.obico.io/docs/user-guides/how-does-detective-hour-work/" target="_blank">how the AI Detection Hour works <i class="fas fa-external-link-alt"></i></a>
              </p>
            </template>

            <!-- detective-hours-pro-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-pro-plan-on-pricing-page'">
              <h3>Pro plan includes 50 AI Detection Hours each month.</h3>
              <ul>
                <li>Unused AI Detection Hours roll over month to month.</li>
                <li>AI Detection Hours expire when subscription ends.</li>
                <li>You can <a href="https://www.obico.io/docs/user-guides/how-does-credits-work/">earn more AI Detection Hours by helping her improve</a>.</li>
                <li>You can also <a class="link" href="#need-more">purchase additional AI hours</a>.</li>
              </ul>
              <p>
                Learn more about
                  <a href="https://www.obico.io/docs/user-guides/how-does-detective-hour-work/" target="_blank">how the AI Detection Hour works <i class="fas fa-external-link-alt"></i></a>
              </p>
            </template>

            <!-- premium-streaming-on-pricing-page -->
            <template v-if="id === 'premium-streaming-on-pricing-page'">
              <div>
                Premium Streaming:
                <ul>
                <li>Up to 25 FPS (frame-per-second)</li>
                <li>Un-throttled</li>
                </ul>
              </div>
              <p>
                Learn more about
                  <a href="https://www.obico.io/docs/user-guides/webcam-streaming-for-human-eyes/" target="_blank">the differences between the Premium Streaming and the Basic Streaming <i class="fas fa-external-link-alt"></i></a>
              </p>
            </template>

            <!-- tunneling-free-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-free-plan-on-pricing-page'">
              <p>Securely tunnel to your OctoPrint from anywhere.</p>
              <p>Free plan is subject to 300MB/month data cap. Data usage is reset on the 1st day of each month.</p>
              <p>
                Learn more about
                  <a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/" target="_blank">OctoPrint Tunneling <i class="fas fa-external-link-alt"></i></a>
              </p>
            </template>

            <!-- tunneling-pro-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-pro-plan-on-pricing-page'">
              <div>Securely tunnel to your OctoPrint from anywhere. Unlimited.</div>
              <p>
                Learn more about
                  <a href="https://www.obico.io/docs/user-guides/octoprint-tunneling/" target="_blank">OctoPrint Tunneling <i class="fas fa-external-link-alt"></i></a>
              </p>
            </template>

            <!-- 3rd-party-app-integration-free-on-pricing-page -->
            <template v-if="id === '3rd-party-app-integration-free-on-pricing-page'">
              <div>
                <div>The monthly cap is shared between 3rd-party app and OctoPrint tunnel:</div>
                <ul>
                  <li>The combined usage can't exceed 300MB per month.</li>
                  <li>Data usage is reset on the 1st day of each month.</li>
                </ul>
                <p>Supported 3rd-party mobile apps:</p>
                <img class="logo-icon"
                  :src="require('@static/img/octoapp.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/printoid.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/octopod.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/polymer.webp')" />
              </div>
            </template>

            <!-- 3rd-party-app-integration-pro-on-pricing-page -->
            <template v-if="id === '3rd-party-app-integration-pro-on-pricing-page'">
              <div>
                <p>Supported 3rd-party mobile apps:</p>
                <img class="logo-icon"
                  :src="require('@static/img/octoapp.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/printoid.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/octopod.webp')" />
                <img class="logo-icon"
                  :src="require('@static/img/polymer.webp')" />
              </div>
            </template>

            <!-- filament-change-on-notification-preferences -->
            <template v-if="id === 'filament-change-on-notification-preferences'">
              <i>
                <ul>Required versions:
                  <li>OctoPrint 1.7.0 or higher</li>
                  <li>The Obico plugin 1.8.11 or higher</li>
                </ul>
              </i>
              <h3>Filament Runout Notifications</h3>
              <p>
                Host_action_commands must be enabled in your firmware to make it possible for your filament runout
                sensor to communicate with OctoPrint and the Obico app. If you enable action commands in
                your firmware, then the filament runout sensor can work properly and the Obico app can notify
                you when the filament runs out. Unfortunately, without host_action_commands enabled, OctoPrint is unable
                to communicate with the printer to know that a filament runout was detected.
              </p>

              <p>To enable support, you need to do the following:</p>
              <ul>
                <li>
                  Marlin: Uncomment #define HOST_ACTION_COMMANDS in Configuration_adv.h and recompile. See here for more
                  information on host_action_commands.
                </li>
              </ul>

              <h3>Color Change Notifications</h3>
              <p>
                Notifications on color change will work with any printer that has M600 enabled in its firmware. You do not
                need host_action_commands enabled to get notified when a color change is needed.
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
.help-wrapper
  display: inline
  position: relative
  text-decoration: underline
  text-decoration-color: var(--color-text-help)
  .text
    display: inline
    &:hover
      cursor: pointer

.widget-wrapper
  $widget-width: 360px
  $x-breakpoint: #{$widget-width + 20px}
  $x-breakpoint-2: #{$widget-width * 2 + 20px}
  position: relative
  left: .1rem
  width: 1rem
  height: 1rem
  display: inline-block

  .question-mark
    display: flex
    color: var(--color-text-help)
    transition: all .2s ease-out
    height: 1rem
    &:hover
      cursor: pointer

    svg
      width: 1rem
      height: 1rem

  .widget
    width: $widget-width
    z-index: 10
    position: absolute
    box-shadow: 0px 3px 30px rgb(0 0 0 / .5)
    border-radius: 12px
    background-color: var(--color-surface-primary)
    display: flex
    flex-direction: column
    color: var(--color-text-primary)

    .logo-icon
      max-height: 50px
      object-fit: contain
      border-radius: 8px
      margin: 0px 15px

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

    .close-button
      $close-btn-height: 24px
      position: absolute
      left: #{$close-btn-height * -.5}
      top: #{$close-btn-height * -.5}
      color: var(--color-text-primary)
      transition: all .2s ease-out
      &:hover
        cursor: pointer
        opacity: .7

      svg
        width: $close-btn-height
        height: $close-btn-height

    .content
      padding: 1rem .875rem
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
