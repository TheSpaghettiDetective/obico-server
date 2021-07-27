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
          <iframe :src="src" frameborder="0"></iframe>
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
 *
 * Don't use like this (it can cause help icon shifting):
 * <help-widget src="...">
 *   <div>Webcam streaming</div>
 * </help-widget>
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
    src: {
      type: String,
      required: true
    },
  },

  methods: {
    // Find preferred direction for widget to pup-up
    // Based on help icon position inside viewport
    positionWidget() {
      const widgetWidth = 360 // should be synced with `$widget-width` in styles
      const widgetHeight = 360 // should be synced with `$widget-height` in styles
      const minHorizontalSpace = widgetWidth + 10
      const minVerticalSpace = widgetHeight + 10

      const helpIconPosition = this.$refs.widgetWrapper.getBoundingClientRect()

      const distanceFromRightEdge = window.innerWidth - (helpIconPosition.left + helpIconPosition.width)
      const distanceFromBottomEdge = window.innerHeight - (helpIconPosition.top + helpIconPosition.height)

      if (distanceFromRightEdge < minHorizontalSpace) {
        this.xDirection = 'right'
      } else {
        this.xDirection = 'left'
      }

      if (distanceFromBottomEdge < minVerticalSpace) {
        this.yDirection = 'bottom'
      } else {
        this.yDirection = 'top'
      }
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.help-wrapper
  position: relative
  text-decoration: underline
  text-decoration-color: rgb(var(--color-text-help))
  .text
    display: inline
    &:hover
      cursor: pointer

.widget-wrapper
  $widget-width: 360px
  $widget-height: 380px
  $widget-header-height: 40px
  $x-breakpoint: #{$widget-width + 20px}
  $x-breakpoint-2: #{$widget-width * 2 + 20px}
  position: relative
  left: .1rem
  width: 1rem
  display: inline-block

  .question-mark
    display: flex
    color: rgb(var(--color-text-help))
    transition: all .2s ease-out
    &:hover
      cursor: pointer

  .widget
    width: $widget-width
    height: $widget-height
    padding-top: $widget-header-height
    z-index: 10
    position: absolute
    -webkit-box-shadow: 0px 3px 30px rgba(0, 0, 0, 0.5) !important
    box-shadow: 0px 3px 30px rgba(0, 0, 0, 0.5) !important
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
      top: 0rem
      bottom: 0rem
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
        padding-left: 12px

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

    iframe
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
