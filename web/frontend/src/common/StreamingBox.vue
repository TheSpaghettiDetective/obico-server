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
        class="text text-warning"
        ref="slowLinkText"
        v-bind:class="{
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
    <div v-if="isVideoVisible && taggedImgAvailable" class="streaming-switch">
      <button type="button" class="btn btn-sm no-corner" :class="{ active: showVideo }" @click="forceStreamingSrc('VIDEO')"><i class="fas fa-video"></i></button>
      <button type="button" class="btn btn-sm no-corner " :class="{ active: !showVideo }" @click="forceStreamingSrc('IMAGE')"><i class="fas fa-camera"></i></button>
    </div>
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
            class="tagged-jpg"
            :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            :src="taggedSrc"
            :alt="printer.name + ' current image'"
          />
        </div>
        <div
          v-show="showVideo"
          id="webrtc-stream"
          class="webcam_fixed_ratio_inner ontop full"
        >
          <video
            ref="video"
            class="remote-video"
            :class="{hide: !isVideoVisible, flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            width=960
            :height="webcamVideoHeight"
            :poster="taggedSrc"
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
import ifvisible from 'ifvisible'

import Janus from '@lib/janus'
import EventBus from '@lib/event_bus'
import webrtc from '@lib/webrtc_streaming'
import printerStockImgSrc from '@static/img/3d_printer.png'

let printerWebRTCUrl = printerId => `/ws/janus/${printerId}/`
let printerSharedWebRTCUrl = token => `/ws/share_token/janus/${token}/`

export default {
  name: 'StreamingBox',
  created() {
    this.webrtc = null

    if (this.isProAccount) {
      Janus.init({
        debug: 'all',
        callback: this.onJanusInitalized
      })
    }

    ifvisible.on('blur', () => {
      if (this.webrtc) {
        this.webrtc.stopStream()
      }
    })

    ifvisible.on('focus', () => {
      if (this.webrtc) {
        this.webrtc.startStream()
      }
    })
  },

  props: {
    printer: {
      type: Object,
      required: true
    },
    shareToken: {
      type: String,
      required: false
    },
    isProAccount: {
      type: Boolean,
      required: true
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
    }
  },

  computed: {
    taggedImgAvailable() {
      return this.taggedSrc !== printerStockImgSrc
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
      return get(this.printer, 'pic.img_url', printerStockImgSrc)
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

    openWebRTCForPrinter() {
      let url, token
      if (this.shareToken) {
        url = printerSharedWebRTCUrl(this.shareToken)
        token = this.shareToken
      } else {
        url = printerWebRTCUrl(this.printer.id)
        token = this.printer.auth_token
      }
      this.webrtc.connect(
        url,
        token
      )
    },

    onJanusInitalized() {
      if (!Janus.isWebrtcSupported()) {
        return
      }

      this.webrtc = webrtc.getWebRTCManager({
        onRemoteStream: this.onWebRTCRemoteStream,
        onCleanup: this.onWebRTCCleanup,
        onSlowLink: this.onSlowLink,
        onTrackMuted: () => this.trackMuted = true,
        onTrackUnmuted: () => this.trackMuted = false,
        onData: this.onWebRTCData,
      })

      EventBus.$on('sendOverDatachannel', this.sendOverDatachannel)

      this.openWebRTCForPrinter()
    },

    onWebRTCRemoteStream(stream) {
      Janus.attachMediaStream(this.$refs.video, stream)

      var videoTracks = stream.getVideoTracks()
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

    onWebRTCData(jsonData) {
      let msg = {}
      try {
        msg = JSON.parse(jsonData)
      } catch {
        // parse error
      }
      if ('passthru' in msg) {
        EventBus.$emit('gotPassthruOverDatachannel', this.printer.id, msg)
      }
    },

    sendOverDatachannel(printerId, msg) {
      if (this.printer && printerId == this.printer.id) {
        if (this.webrtc && this.webrtc.streaming) {
          this.webrtc.streaming.data({text: JSON.stringify(msg), success: () => {}})
        }
      }
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

      this.$swal({
        title: 'Video frames dropped',
        html: `
          <p>The video frames are getting dropped because there is a bandwidth bottleneck along the route it they take to travel from your Raspberry Pi to your computer. The bottleneck can be anywhere but in most cases <Text bold>it's either your computer's internet connection, or your Raspberry Pi's</Text>.</p>
          <p>Make sure your computer is connected to the same network as your Pi. If you still see this warning, you need to trouble-shoot your computer's Wi-Fi connection, probably by moving closer to the Wi-Fi router.</p>
          <p>If the webcam stream is smooth when your computer is on the same Wi-Fi network as your Pi, the bottleneck is likely with the upload speed of your internet connection. You need to run a speed test to make sure you have high-enough upload speed, as well as <b>low latency (ping)</b>.</p>
          <p>Check out <a target="_blank" href="https://www.thespaghettidetective.com/docs/webcam-feed-is-laggy/">the step-by-step trouble-shooting guide.</a></p>
        `,
        showCloseButton: true,
      })
    },

    showMutedStatusDescription(event) {
      event.preventDefault()

      this.$swal({
        title: 'Webcam stream buffering',
        html: `
          <p>When you see the messaging about webcam stream is "buffering" occassionaly, you can just reload the page. If this message repeatedly appears, it usually indicates a constricted video stream on <strong>your Raspberry Pi, not your computer</strong>.</p>
          <p>The most common reasons are:</p>
          <ul>
            <li>Camera resolution is set too high.</li>
            <li>Camera framerate is set too high. This is only when you set <a target="_blank" href="https://www.thespaghettidetective.com/docs/streaming-compatibility-mode/">the compatibility mode</a> to "always".</li>
            <li>The upload speed of your Raspberry Pi is too low.</li>
          </ul>
          <br>
          <p>You should leave the compatibility mode to "auto", unless you have <a target="_blank" href="https://www.thespaghettidetective.com/docs/streaming-compatibility-mode/#are-there-situations-when-i-want-to-always-stream-in-compatibility-mode">a good reason to it to "always".</a></p>
          <p>As a rule of thumb, for every 300k-pixel resolution (640x480), you need to have 1.5Mbps upload bandwidth to stream smoothly at 25fps. This means if you set the webcam resolution to 1024x768 (~800k pixels), you need to have 4.5Mbps upload bandwidth. Also remember that the upload bandwidth of your Raspberry Pi may not be the same as your computer, even if they are connected to the same Wi-Fi network. This is because Raspberry Pi's Wi-Fi chip is weaker than the most computers'.</p>
        `,
        showCloseButton: true,
      })
    }
    /** End of video warning handling */
  },
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.loading-icon
  position: absolute
  width: 3rem
  height: 3rem
  top: calc(50% - 1.5rem)
  left: calc(50% - 1.5rem)
  z-index: 100

.streaming-switch
  background-color: rgba(255, 255, 255, 0.4)
  border: solid thin #888
  position: absolute
  display: flex
  flex-flow: column
  right: 4px
  top: 4px
  z-index: 100

  .btn
    color: #444444
    &.active
      color: #ffffff
      background-color: rgba(0,0,0,0.6)

.slow-link-wrapper
  $height: 24px
  position: absolute
  height: $height
  z-index: 10
  background-color: theme.$white
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
    color: theme.$white

.muted-status-wrapper
  position: absolute
  width: 100%
  z-index: 10
  bottom: 0
  left: 0
  background-color: rgba(0,0,0,.6)
  text-align: center
  padding: 10px 0
</style>
