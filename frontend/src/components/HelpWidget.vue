<template>
  <div
    v-click-outside="() => (show = false)"
    class="help-wrapper"
    :class="{ highlighted: highlight }"
  >
    <!-- Slot for text -->
    <div
      class="text"
      @click="
        positionWidget()
        show = !show
      "
    >
      <slot></slot>
    </div>

    <div ref="widgetWrapper" class="widget-wrapper">
      <!-- Help icon -->
      <div
        class="question-mark"
        @click="
          positionWidget()
          show = !show
        "
      >
        <svg>
          <use href="#svg-question-icon" />
        </svg>
      </div>

      <!-- Help widget -->
      <transition name="pop-up">
        <div v-show="show" ref="widget" class="widget" :class="[xDirection, yDirection]">
          <div v-if="showCloseButton" class="close-button" @click="show = false">
            <svg width="16" height="16">
              <use href="#svg-cross-icon" />
            </svg>
          </div>

          <!-- Help content -->
          <div class="content">
            <!-- KINGROON PRICING PAGE HELP CONTENT START -->
            <!-- basic-streaming-on-kingroon-pricing-page -->
            <template v-if="id === 'basic-streaming-on-kingroon-pricing-page'">
              <div>
                {{$t("Basic Streaming")}}:
                <ul>
                  <li>{{ $t("1 FPS (frame-per-second), 100 hours of streaming per month") }}</li>
                </ul>
              </div>
              <div>
                <i18next :translation="$t('Learn more about {localizedDom}')">
                  <template #localizedDom>
                    <a href="https://docs.kingroon.com/docs/user-guides/webcam-streaming-for-human-eyes/" target="_blank">{{$t("the differences between the Premium Streaming and the Basic Streaming")}} <i class="fas fa-external-link-alt"></i></a>
                  </template>
                </i18next>

              </div>
            </template>

            <!-- detective-hours-free-plan-on-kingroon-pricing-page -->
            <template v-if="id === 'detective-hours-free-plan-on-kingroon-pricing-page'">
                <p>{{ $t("Basic AI Detection checks for failures every 30 seconds.") }}</p>
                <p>{{ $t("AI usage is reset on the 1st of each month. Hours do not roll over month to month.") }}</p>
              <p>
                {{$t("Learn more about")}}
                <a
                  href="https://www.docs.kingroon.com/docs/user-guides/how-does-detective-hour-work/"
                  target="_blank"
                  >{{ $t("how the AI Detection Hour works ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- tunneling-free-plan-on-kingroon-pricing-page -->
            <template v-if="id === 'tunneling-free-plan-on-kingroon-pricing-page'">
              <p>{{ $t("Securely tunnel to your Mainsail or fluidd Klipper interface from anywhere.") }}</p>
              <p>
                {{$t("Free plan is subject to 300MB/month data cap. Data usage is reset on the 1st day of each month.")}}
              </p>
              <p>
                {{$t("Learn more about")}}
                <a href="https://docs.kingroon.com/docs/user-guides/octoprint-tunneling/" target="_blank"
                  >{{ $t("Klipper tunnel ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- premium-streaming-on-kingroon-pricing-page -->
            <template v-if="id === 'premium-streaming-on-kingroon-pricing-page'">
              <div>
                {{$t("Premium Streaming")}}:
                <ul>
                  <li>{{ $t("Up to 25 FPS (frame-per-second)") }}</li>
                  <li>{{ $t("Up to 5 FPS with any webcam") }}</li>
                  <li>{{ $t("Up to 25 FPS with Kingroon H.264 Camera.") }}</li>
                </ul>
              </div>
              <p>
                {{$t("Learn more about")}}
                <a
                  href="https://docs.kingroon.com/docs/user-guides/webcam-streaming-for-human-eyes/"
                  target="_blank"
                  >{{$t("the differences between the Premium Streaming and the Basic Streaming")}}
                  <i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- detective-hours-pro-plan-on-kingroon-pricing-page -->
            <template v-if="id === 'detective-hours-pro-plan-on-kingroon-pricing-page'">
              <p>{{ $t("Advanced AI checks for failures more frequently - Catch failures up to 2X faster than Basic AI.") }}</p>
              <p>{{ $t("Unused AI Detection Hours roll over month-to-month") }}</p>
              <p>
                {{$t("Learn more about")}}
                <a
                  href="https://www.docs.kingroon.com/docs/user-guides/how-does-detective-hour-work/"
                  target="_blank"
                  >{{ $t("how the AI Detection Hour works ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- tunneling-pro-plan-on-kingroon-pricing-page -->
            <template v-if="id === 'tunneling-pro-plan-on-kingroon-pricing-page'">
              <div>{{ $t("Securely tunnel to your Mainsail or fluidd Klipper interface from anywhere. Unlimited.") }}</div>
              <p>
                {{$t("Learn more about")}}
                <a href="https://docs.kingroon.com/docs/user-guides/octoprint-tunneling/" target="_blank"
                  >{{ $t("Klipper tunnel ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- KINGROON PRICING PAGE HELP CONTENT END -->

            <!-- basic-streaming-on-pricing-page -->
            <template v-if="id === 'basic-streaming-on-pricing-page'">
              <div>
                {{$t("Basic Streaming")}}:
                <ul>
                  <li>{{ $t("Up to 5 FPS (frame-per-second)") }}</li>
                  <li>{{ $t("Throttled for 30 seconds every minute") }}</li>
                </ul>
              </div>
              <div>
                <i18next :translation="$t('Learn more about {localizedDom}')">
                  <template #localizedDom>
                    <a :href="getDocUrl('/user-guides/webcam-streaming-for-human-eyes/')" target="_blank">{{$t("the differences between the Premium Streaming and the Basic Streaming")}} <i class="fas fa-external-link-alt"></i></a>
                  </template>
                </i18next>

              </div>
            </template>

            <!-- detective-hours-free-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-free-plan-on-pricing-page'">
              <h3>{{ $t("Yup! Even Free account gets 10 AI Detection Hours for FREE each month.") }}</h3>
              <ul>
                <li>{{ $t("Unused AI Detection Hours roll over month to month.") }}</li>
                <li>
                  {{$t("You can")}}
                  <a :href="getDocUrl('/user-guides/how-does-credits-work/')"
                    >{{ $t("earn free AI Detection Hours by helping her improve") }}</a
                  >.
                </li>
                <li>
                  {{$t("You can also")}} <a class="link" href="#need-more">{{ $t("purchase additional AI hours") }}</a>.
                </li>
              </ul>
              <p>
                {{$t("Learn more about")}}
                <a
                  :href="getDocUrl('/user-guides/how-does-detective-hour-work/')"
                  target="_blank"
                  >{{ $t("how the AI Detection Hour works ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- detective-hours-pro-plan-on-pricing-page -->
            <template v-if="id === 'detective-hours-pro-plan-on-pricing-page'">
              <h3>{{ $t("Pro plan includes 50 AI Detection Hours each month.") }}</h3>
              <ul>
                <li>{{ $t("Unused AI Detection Hours roll over month to month.") }}</li>
                <li>{{ $t("AI Detection Hours expire when subscription ends.") }}</li>
                <li>
                  {{$t("You can")}}
                  <a :href="getDocUrl('/user-guides/how-does-credits-work/')"
                    >{{ $t("earn more AI Detection Hours by helping her improve") }}</a
                  >.
                </li>
                <li>
                  {{$t("You can also")}} <a class="link" href="#need-more">{{ $t("purchase additional AI hours") }}</a>.
                </li>
              </ul>
              <p>
                {{$t("Learn more about")}}
                <a
                  :href="getDocUrl('/user-guides/how-does-detective-hour-work/')"
                  target="_blank"
                  >{{ $t("how the AI Detection Hour works ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- premium-streaming-on-pricing-page -->
            <template v-if="id === 'premium-streaming-on-pricing-page'">
              <div>
                {{$t("Premium Streaming")}}:
                <ul>
                  <li>{{ $t("Up to 25 FPS (frame-per-second)") }}</li>
                  <li>{{ $t("Un-throttled") }}</li>
                </ul>
              </div>
              <p>
                {{$t("Learn more about")}}
                <a
                  :href="getDocUrl('/user-guides/webcam-streaming-for-human-eyes/')"
                  target="_blank"
                  >{{$t("the differences between the Premium Streaming and the Basic Streaming")}}
                  <i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- tunneling-free-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-free-plan-on-pricing-page'">
              <p>{{ $t("Securely tunnel to your OctoPrint/Klipper from anywhere.") }}</p>
              <p>
                {{$t("Free plan is subject to 300MB/month data cap. Data usage is reset on the 1st day of each month.")}}
              </p>
              <p>
                {{$t("Learn more about")}}
                <a :href="getDocUrl('/user-guides/octoprint-tunneling/')" target="_blank"
                  >{{ $t("OctoPrint/Klipper tunnel ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- tunneling-pro-plan-on-pricing-page -->
            <template v-if="id === 'tunneling-pro-plan-on-pricing-page'">
              <div>{{ $t("Securely tunnel to your OctoPrint/Klipper from anywhere. Unlimited.") }}</div>
              <p>
                {{$t("Learn more about")}}
                <a :href="getDocUrl('/user-guides/octoprint-tunneling/')" target="_blank"
                  >{{ $t("OctoPrint/Klipper tunnel ") }}<i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <!-- 3rd-party-app-integration-free-on-pricing-page -->
            <template v-if="id === '3rd-party-app-integration-free-on-pricing-page'">
              <div>
                <div>{{ $t("The monthly cap is shared between 3rd-party app and OctoPrint tunnel") }}:</div>
                <ul>
                  <li>{{ $t("The combined usage can't exceed 300MB per month.") }}</li>
                  <li>{{ $t("Data usage is reset on the 1st day of each month.") }}</li>
                </ul>
                <p>{{ $t("Supported 3rd-party mobile apps") }}:</p>
                <img class="logo-icon" :src="require('@static/img/octoapp.webp')" />
                <img class="logo-icon" :src="require('@static/img/printoid.webp')" />
                <img class="logo-icon" :src="require('@static/img/octopod.webp')" />
                <img class="logo-icon" :src="require('@static/img/polymer.webp')" />
              </div>
            </template>

            <!-- 3rd-party-app-integration-pro-on-pricing-page -->
            <template v-if="id === '3rd-party-app-integration-pro-on-pricing-page'">
              <div>
                <p>{{ $t("Supported 3rd-party mobile apps") }}:</p>
                <img class="logo-icon" :src="require('@static/img/octoapp.webp')" />
                <img class="logo-icon" :src="require('@static/img/printoid.webp')" />
                <img class="logo-icon" :src="require('@static/img/octopod.webp')" />
                <img class="logo-icon" :src="require('@static/img/polymer.webp')" />
              </div>
            </template>

            <!-- filament-change-on-notification-preferences -->
            <template v-if="id === 'filament-change-on-notification-preferences'">
              <i>
                <ul>
                  {{$t("Required versions")}}:
                  <li>{{ $t("OctoPrint 1.7.0 or higher") }}</li>
                  <li>{{$t("The {brandName} plugin 1.8.11 or higher",{brandName: $syndicateText.brandName })}}</li>
                </ul>
              </i>
              <h3>{{ $t("Filament Runout Notifications") }}</h3>
              <p>
                {{ $t('Host_action_commands must be enabled in your firmware to make it possible for your filament runout sensor to communicate with OctoPrint and the {brandName} app. If you enable action commands in your firmware, then the filament runout sensor can work properly and the {brandName} app can notify you when the filament runs out. Unfortunately, without host_action_commands enabled, OctoPrint is unable to communicate with the printer to know that a filament runout was detected.',{brandName:$syndicateText.brandName}) }}
              </p>

              <p>{{ $t("To enable support, you need to do the following") }}:</p>
              <ul>
                <li>
                  {{$t("Marlin: Uncomment #define HOST_ACTION_COMMANDS in Configuration_adv.h and recompile. See here for more information on host_action_commands.")}}
                </li>
              </ul>

              <h3>{{ $t("Color Change Notifications") }}</h3>
              <p>
                {{$t("Notifications on color change will work with any printer that has M600 enabled in its firmware. You do not need host_action_commands enabled to get notified when a color change is needed.")}}
              </p>
            </template>

            <!-- filament-used-may-be-incorrect -->
            <template v-if="id === 'filament-used-may-be-incorrect'">
              <h3>{{ $t("Is filament usage inaccurate?") }}</h3>
              <p>
                {{ $t('G-code files uploaded to your {brandName} account before upgrading to {brandName} for OctoPrint version 2.3.0 or {brandName} for Klipper version 1.2.0 do not include filament usage data.',{brandName:$syndicateText.brandName}) }}
              </p>
              <p><strong>{{ $t("To ensure accurate filament usage and other statistics") }}:</strong></p>
              <ul>
                <li>
                  {{ $t('Upload G-code files and start prints directly through {brandName} instead of OctoPrint/Klipper.',{brandName:$syndicateText.brandName}) }}

                </li>
                <li>
                  {{$t("Use a slicer that supports filament usage parameters, such as Cura, Prusa Slicer, SuperSlicer, IdeaMaker, or Simplify3D.")}}
                </li>
                <li>
                  {{$t("Print statistics for G-code files deleted before 12/20/2022 are not included. For files deleted after 12/20/2022, statistics are preserved.")}}
                </li>
              </ul>
            </template>

            <!-- thumbnail-setup-guide -->
            <template v-if="id === 'thumbnail-setup-guide'">
              <p>
                <a :href="getDocUrl('/user-guides/enable-gcode-thumbnails/')" target="_blank"
                  >{{$t("Learn how to configure G-Code preview generation in your slicer")}}
                  <i class="fas fa-external-link-alt"></i
                ></a>
              </p>
            </template>

            <template v-if="id === 'fan-speed-widget-help'">
              <p>
                {{$t("Adjust the speed of the cooling fan by setting a percentage value between 0 and 100. The default value is usually 100, which means the fan will run at full speed. Lowering the fan speed can reduce noise and save energy, but may also affect print quality if the printer gets too hot.")}}
              </p>
            </template>
            <template v-if="id === 'print-speed-widget-help'">
              <p>
                {{$t("Adjust the speed of your 3D printer by changing the speed of all movement commands by a specified factor. The default value is 100%, meaning that the printer will move at its standard speed. Lowering the print speed factor will slow down your print, while increasing it will speed it up. Value of 200% will double the speed.")}}
              </p>
            </template>
            <template v-if="id === 'flow-rate-widget-help'">
              <p>
                {{$t("Flow rate is the speed at which the printer extrudes plastic. If the flow rate is too high, the printer may extrude too much plastic and create blobs or stringing, while too low flow rate may result in weak and brittle prints. Adjusting the flow rate can help achieve the optimal balance between speed and quality. The default value is 100%.")}}
              </p>
            </template>

            <!-- coupon-entered-automatically -->
            <template v-if="id === 'coupon-entered-automatically'">
              <div>
                <p>{{ $t('No cost for three months. Plan renews after expiration. Cancel anytime.') }}</p>
              </div>
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

  directives: {
    ClickOutside,
  },

  props: {
    id: {
      type: String,
      required: true,
    },
    highlight: {
      type: Boolean,
      default: true,
    },
    showCloseButton: {
      type: Boolean,
      default: false,
    },
    textBefore: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      show: false,
      xDirection: 'left',
      yDirection: 'top',
    }
  },

  methods: {
    // Find preferred direction for widget to pup-up
    // Based on help icon position inside viewport
    positionWidget() {
      this.$nextTick(() => {
        const widgetWidth = this.$refs.widget?.offsetWidth || 360
        const widgetHeight = this.$refs.widget?.offsetHeight || 420

        const minHorizontalSpace = widgetWidth + 10
        const minVerticalSpace = widgetHeight + 10

        const helpIconPosition = this.$refs.widgetWrapper.getBoundingClientRect()
        const distanceFromRightEdge =
          window.innerWidth - (helpIconPosition.left + helpIconPosition.width)
        const distanceFromBottomEdge =
          window.innerHeight - (helpIconPosition.top + helpIconPosition.height)

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
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.help-wrapper
  display: inline
  position: relative
  &.highlighted
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
  top: .1rem
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
    box-shadow: 0 0 0 9999px rgb(0 0 0 / 0.5)
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

.pop-up-enter,
.pop-up-leave-to {
  transform: translate(-2rem, -1rem) scale(0.8);
  opacity: 0;
}
</style>
