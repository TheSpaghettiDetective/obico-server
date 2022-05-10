<template>
  <div class="card-img-top webcam_container">
    <div
      v-show="slowLinkLoss > 50"
      class="slow-link-wrapper"
      ref="slowLinkWrapper"
      @click="slowLinkClicked"
      @mouseenter="fixSlowLinkTextWidth(); slowLinkShowing = true; slowLinkHiding = false;"
      @mouseleave="fixSlowLinkTextWidth(); slowLinkShowing = false; slowLinkHiding = true;"
    >
      <div class="icon bg-warning">
        <i class="fas fa-exclamation"></i>
      </div>
      <div
        class="text"
        ref="slowLinkText"
        :class="{
          'show-and-hide': !slowLinkShowing && !slowLinkHiding,
          'showing': slowLinkShowing && !slowLinkHiding,
          'hiding': !slowLinkShowing && slowLinkHiding}"
      >Video frames dropped</div>
    </div>
    <div v-show="trackMuted" class="muted-status-wrapper">
      <div class="text">Buffering...</div>
      <a href="#" @click="showMutedStatusDescription($event)">Why is it stuck?</a>
    </div>
    <b-spinner v-if="trackMuted || videoLoading" class="loading-icon" label="Buffering..."></b-spinner>

    <b-dropdown v-if="isVideoVisible && taggedImgAvailable" class="streaming-switch" right no-caret toggle-class="icon-btn">
      <template #button-content>
        <i class="fas fa-ellipsis-v"></i>
      </template>
      <b-dropdown-item href="#" @click.prevent="forceStreamingSrc(null)">
        <span class="title" :class="{'active': stickyStreamingSrc === null}">
          <i class="fas fa-check" v-show="stickyStreamingSrc === null"></i>
          Auto
        </span><br>
        <span class="description">Show the best quality stream that is available</span>
      </b-dropdown-item>
      <b-dropdown-divider></b-dropdown-divider>
      <b-dropdown-item href="#" @click.prevent="forceStreamingSrc('VIDEO')">
        <span class="title" :class="{'active': stickyStreamingSrc === 'VIDEO'}">
          <i class="fas fa-check" v-show="stickyStreamingSrc === 'VIDEO'"></i>
          Premium webcam streaming view
        </span><br>
        <span class="description">Premium-only feature (25 fps)</span>
      </b-dropdown-item>
      <div class="dropdown-divider"></div>
      <b-dropdown-item href="#" @click.prevent="forceStreamingSrc('IMAGE')">
        <span class="title" :class="{'active': stickyStreamingSrc === 'IMAGE'}">
          <i class="fas fa-check" v-show="stickyStreamingSrc === 'IMAGE'"></i>
          Failure detection view
        </span><br>
        <span class="description">Shows detection boxes if present (0.1 fps)</span>
      </b-dropdown-item>
    </b-dropdown>

    <div
      :class="webcamRotateClass"
    >
      <div
        class="webcam_fixed_ratio"
        :class="webcamRatioClass"
      >
        <div
          class="webcam_fixed_ratio_inner full"
        >
          <img
            v-if="taggedSrc !== printerStockImgSrc"
            class="tagged-jpg"
            :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            :src="taggedSrc"
            :alt="printer.name + ' current image'"
          />
          <svg v-else class="poster-placeholder">
            <use :href="printerStockImgSrc" />
          </svg>
        </div>
        <div
          v-show="showVideo"
          class="webcam_fixed_ratio_inner ontop full"
        >
          <video
            ref="video"
            class="remote-video"
            :class="{hide: !isVideoVisible, flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            width=960
            :height="webcamVideoHeight"
            :poster="taggedSrc !== printerStockImgSrc ? taggedSrc : ''"
            autoplay muted playsinline
            @loadstart="onLoadStart()"
            @canplay="onCanPlay()"
          ></video>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'

import Janus from '@src/lib/janus'

export default {
  name: 'StreamingBox',
  created() {
    if (this.webrtc) {
      this.webrtc.callbacks = {
        ...this.webrtc.callbacks,
        onRemoteStream: this.onWebRTCRemoteStream,
        onCleanup: this.onWebRTCCleanup,
        onSlowLink: this.onSlowLink,
        onTrackMuted: () => this.trackMuted = true,
        onTrackUnmuted: () => this.trackMuted = false,
      }
    }
  },

  props: {
    printer: {
      type: Object,
      required: true
    },
    webrtc: {
      type: Object,
      required: false,
    },
  },

  data() {
    return {
      stickyStreamingSrc: null,
      isVideoVisible: false,
      slowLinkLoss: 0,
      slowLinkShowing: false, // show on mousenter
      slowLinkHiding: false, // hide on moseleave
      trackMuted: false,
      videoLoading: false,
      printerStockImgSrc: '#svg-3d-printer'
    }
  },

  computed: {
    taggedImgAvailable() {
      return this.taggedSrc !== this.printerStockImgSrc
    },
    showVideo() {
      return this.isVideoVisible && this.stickyStreamingSrc !== 'IMAGE'
    },
    webcamRotateClass() {
      switch (this.printer.settings.webcam_rotate90) {
      case true:
        return 'webcam_rotated'
      case false:
        return 'webcam_unrotated'
      default:
        return 'webcam_unrotated'
      }
    },
    webcamRatioClass() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 'ratio169'
      case false:
        return 'ratio43'
      default:
        return 'ratio43'
      }
    },
    webcamVideoHeight() {
      switch (this.printer.settings.ratio169) {
      case true:
        return 540
      case false:
        return 720
      default:
        return 720
      }
    },
    taggedSrc() {
      return get(this.printer, 'pic.img_url', this.printerStockImgSrc)
    },
  },

  methods: {
    forceStreamingSrc(src) {
      this.stickyStreamingSrc = src
    },
    onCanPlay() {
      this.videoLoading = false
    },
    onLoadStart() {
      this.videoLoading = true
    },

    onWebRTCRemoteStream(stream) {
      Janus.attachMediaStream(this.$refs.video, stream)

      const videoTracks = stream.getVideoTracks()
      if (videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
        // No remote video
        this.isVideoVisible = false
      } else {
        this.isVideoVisible = true
      }
    },

    onWebRTCCleanup() {
      this.isVideoVisible = false
    },

    /** Video warning handling */

    fixSlowLinkTextWidth() {
      const width = window.getComputedStyle(this.$refs.slowLinkText).width
      this.$refs.slowLinkText.style.width = width
    },

    onSlowLink(loss) {
      this.slowLinkLoss += loss
    },

    slowLinkClicked() {
      this.slowLinkShowing = false
      this.slowLinkHiding = false
      this.slowLinkLoss = 0

      this.$swal.Prompt.fire({
        title: 'Video frames dropped',
        html: `
          <p>The video frames are getting dropped because there is a bandwidth bottleneck along the route it they take to travel from your Raspberry Pi to your computer. The bottleneck can be anywhere but in most cases <Text bold>it's either your computer's internet connection, or your Raspberry Pi's</Text>.</p>
          <p>Make sure your computer is connected to the same network as your Pi. If you still see this warning, you need to trouble-shoot your computer's Wi-Fi connection, probably by moving closer to the Wi-Fi router.</p>
          <p>If the webcam stream is smooth when your computer is on the same Wi-Fi network as your Pi, the bottleneck is likely with the upload speed of your internet connection. You need to run a speed test to make sure you have high-enough upload speed, as well as <b>low latency (ping)</b>.</p>
          <p>Check out <a target="_blank" href="https://www.obico.io/docs/user-guides/webcam-feed-is-laggy/">the step-by-step trouble-shooting guide.</a></p>
        `,
        showCloseButton: true,
      })
    },

    showMutedStatusDescription(event) {
      event.preventDefault()

      this.$swal.Prompt.fire({
        title: 'Webcam stream buffering',
        html: `
          <p>When you see the messaging about webcam stream is "buffering" occasionally, you can just reload the page. If this message repeatedly appears, it may indicate one of the problems:</p>
          <p class="lead">1. A constricted video stream on <strong>your Raspberry Pi. The most common reasons are:</p>
          <ul>
            <li>Camera resolution is set too high.</li>
            <li>Camera framerate is set too high.</li>
            <li>The upload speed of your Raspberry Pi is too low.</li>
          </ul>
          <p class="lead">2. The internet connection of your computer or phone is not fast enough.</p>
          <p class="lead">3. Your webcam is not properly connected to your Raspberry Pi.</p>
          <br>
          <p>Check <a target="_blank" href="https://www.obico.io/docs/user-guides/webcam-feed-is-laggy">this step-by-step troubleshooting guide</a>.</p>
        `,
        showCloseButton: true,
      })
    }
    /** End of video warning handling */
  },
}
</script>

<style lang="sass" scoped>
.loading-icon
  position: absolute
  width: 3rem
  height: 3rem
  top: calc(50% - 1.5rem)
  left: calc(50% - 1.5rem)
  z-index: 99

.streaming-switch
  position: absolute
  right: 20px
  top: 20px
  z-index: 99

  .dropdown-item
    .title.active
      color: var(--color-primary)
      i
        margin-right: 2px

    .description
      font-size: 0.8em
      opacity: .5

  .btn
    overflow: hidden
    color: #fff !important
    opacity: .8
    &:hover, &:focus
      opacity: 1

.slow-link-wrapper
  $height: 24px
  position: absolute
  height: $height
  z-index: 10
  background-color: rgb(0 0 0 / .2)
  border-radius: $height
  top: 10px
  left: 10px
  padding-left: $height
  line-height: $height
  font-size: 14px
  width: auto

  &:hover
    cursor: pointer

  .text
    width: 0
    height: $height
    overflow: hidden
    text-align: center
    opacity: 0

    &.show-and-hide
      animation-name: showAndHideText
      animation-duration: 3s

    &.showing
      animation-name: showText
      animation-duration: .4s
      animation-fill-mode: forwards

    &.hiding
      animation-name: hideText
      animation-duration: .4s
      animation-fill-mode: forwards

    $widthFull: 160px
    $paddingRightFull: 10px

    @keyframes showText
      from
        opacity: 0
      99%
        width: $widthFull
        padding-right: $paddingRightFull
        opacity: 0
      to
        width: $widthFull
        padding-right: $paddingRightFull
        opacity: 1

    @keyframes hideText
      from
        opacity: 1
      1%
        opacity: 0
      to
        width: 0
        padding-right: 0
        opacity: 0

    @keyframes showAndHideText
      0%
        width: 0
        opacity: 0
      19%
        width: $widthFull
        padding-right: $paddingRightFull
        opacity: 0
      20%
        opacity: 1
      80%
        opacity: 1
        width: $widthFull
        padding-right: $paddingRightFull
      81%
        opacity: 0
      100%
        width: 0
        padding-right: 0
        opacity: 0

  .icon
    width: 20px
    height: 20px
    border-radius: 10px
    position: absolute
    top: 2px
    left: 2px
    font-size: 12px
    line-height: 20px
    text-align: center
    color: var(--color-on-warning)

.muted-status-wrapper
  position: absolute
  width: 100%
  z-index: 10
  bottom: 0
  left: 0
  background-color: var(--color-overlay)
  text-align: center
  padding: 10px 0

.poster-placeholder
  $size: 150px
  color: rgb(255 255 255 / .2)
  width: $size
  height: $size
  position: absolute
  left: calc(50% - #{$size / 2})
  top: calc(50% - #{$size / 2})
</style>
