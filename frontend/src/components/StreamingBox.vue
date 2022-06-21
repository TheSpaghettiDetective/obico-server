<template>
  <div class="card-img-top webcam_container">

    <!-- Video frames dropped -->
    <div
      v-show="slowLinkLoss > slowLinkLossLimit"
      class="slow-link-wrapper"
      ref="slowLinkWrapper"
      @click="onSlowLinkClick"
      @mouseenter="fixSlowLinkTextWidth(); isSlowLinkShowing = true; isSlowLinkHiding = false;"
      @mouseleave="fixSlowLinkTextWidth(); isSlowLinkShowing = false; isSlowLinkHiding = true;"
    >
      <div class="icon bg-warning">
        <i class="fas fa-exclamation"></i>
      </div>
      <div
        ref="slowLinkText"
        class="text"
        :class="{
          'show-and-hide': !isSlowLinkShowing && !isSlowLinkHiding,
          'showing': isSlowLinkShowing && !isSlowLinkHiding,
          'hiding': !isSlowLinkShowing && isSlowLinkHiding
        }"
      >Video frames dropped</div>
    </div>

    <!-- Buffering -->
    <div v-show="isTrackMuted" class="muted-status-wrapper">
      <div class="text">Buffering...</div>
      <a href="#" @click.prevent="onMutedStatusClick">Why is it stuck?</a>
    </div>

    <!-- Loading spinner -->
    <b-spinner v-if="isTrackMuted || isVideoLoading" class="centered-element" label="Buffering..."></b-spinner>

    <!-- Play button -->
    <b-button
      v-if="isBasicStreamingReadyToPlay || isBasicStreamingFrozen"
      @click="startActiveSession"
      class="centered-element p-0"
      :disabled="isBasicStreamingFrozen"
    >
      <i class="fas fa-play ml-1" v-if="isBasicStreamingReadyToPlay"></i>
      <span class="medium text-bold" v-if="isBasicStreamingFrozen">{{frozenSessionRemainingSeconds}}s</span>
    </b-button>

    <!-- Countdown and bitrate -->
    <div
      v-if="isBasicStreamingInProgress || currentBitrate"
      class="streaming-info overlay-info small"
      :class="{'clickable': isBasicStreamingInProgress}"
      @click="onInfoClicked"
    >
      <div v-if="isBasicStreamingInProgress" class="text-success">{{activeSessionRemainingSeconds}}</div>
      <div v-if="currentBitrate">{{currentBitrate}}</div>
    </div>

    <!-- Free streaming info -->
    <div
      v-if="isBasicStreamingReadyToPlay || isBasicStreamingFrozen"
      class="streaming-guide overlay-info"
      @click="onInfoClicked"
    >
      <div class="message" v-if="isBasicStreamingReadyToPlay">Webcam streams up to 5 FPS for Free</div>
      <div class="message text-warning" v-if="isBasicStreamingFrozen">{{frozenSessionRemainingSeconds}}s left in the cooldown period</div>
      <a href="#" class="learn-more">Learn more...</a>
    </div>

    <!-- Video -->
    <div :class="webcamRotateClass">
      <div class="webcam_fixed_ratio" :class="webcamRatioClass">
        <div class="webcam_fixed_ratio_inner full">
          <img
            v-if="webcamSnapshot"
            class="tagged-jpg"
            :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            :src="webcamSnapshot"
            :alt="printer.name + ' current image'"
          />
          <svg v-else class="poster-placeholder">
            <use href="#svg-3d-printer" />
          </svg>
        </div>
        <div v-show="streamStatus === STREAM_STATUS.Started" class="webcam_fixed_ratio_inner ontop full">
          <video
            ref="video"
            class="remote-video"
            :class="{flipH: printer.settings.webcam_flipH, flipV: printer.settings.webcam_flipV}"
            width=960
            :height="webcamVideoHeight"
            :poster="webcamSnapshot"
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
import ifvisible from 'ifvisible'
import Janus from '@src/lib/janus'
import { StreamThrottle, STREAM_SESSION, STREAM_EVENT } from '@src/lib/stream-throttle'
import { isLocalStorageSupported } from '@static/js/utils'

const STREAM_STATUS = {
  Unavailable: 'Unavailable',
  Available: 'Available',
  Started: 'Started',
}

export default {
  name: 'StreamingBox',

  created() {
    if (this.webrtc) {
      this.webrtc.callbacks = {
        ...this.webrtc.callbacks,
        onStreamAvailable: this.onStreamAvailable,
        onRemoteStream: this.onWebRTCRemoteStream,
        onCleanup: this.onWebRTCCleanup,
        onSlowLink: this.onSlowLink,
        onTrackMuted: () => this.isTrackMuted = true,
        onTrackUnmuted: () => this.isTrackMuted = false,
        onBitrateUpdated: (bitrate) => this.currentBitrate = bitrate.value,
      }

      if (!this.autoplay) {
        this.streamThrottle = new StreamThrottle(this.printer.id, isLocalStorageSupported() ? localStorage : null)
      }

      ifvisible.on('blur', () => {
        if (this.webrtc) {
          this.webrtc.stopStream()
        }
      })

      ifvisible.on('focus', () => {
        if (this.webrtc && this.autoplay) {
          this.webrtc.startStream()
        }
      })
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
    autoplay: {
      type: Boolean,
      required: true,
    }
  },

  data() {
    return {
      STREAM_STATUS,
      streamStatus: STREAM_STATUS.Unavailable,
      isTrackMuted: false,
      isVideoLoading: false,

      slowLinkLoss: 0,
      slowLinkLossLimit: 50,
      isSlowLinkShowing: false,  // show on mousenter
      isSlowLinkHiding: false,  // hide on moseleave
      currentBitrate: null,

      remainingSeconds: StreamThrottle.defaultRemainingSeconds(),
      activeSessionRemainingSeconds: StreamThrottle.calculateSessionsSeconds()[0],
      frozenSessionRemainingSeconds: StreamThrottle.calculateSessionsSeconds()[1],
      basicStreamTimerId: null,
      currentSession: STREAM_SESSION.Idle,
    }
  },

  computed: {
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
    webcamSnapshot() {
      return this.printer?.pic?.img_url
    },

    // Free user streaming
    isBasicStreamingInProgress() {
      return !this.autoplay && this.currentSession === STREAM_SESSION.Active
    },
    isBasicStreamingReadyToPlay() {
      return !this.autoplay && this.streamStatus === STREAM_STATUS.Available && !this.isTrackMuted && !this.isVideoLoading &&
        this.currentSession === STREAM_SESSION.Idle
    },
    isBasicStreamingFrozen() {
      return !this.autoplay && this.streamStatus === STREAM_STATUS.Available && this.currentSession === STREAM_SESSION.Frozen
    },
  },

  watch: {
    remainingSeconds(newSeconds, _) {
      this.currentSession = StreamThrottle.currentSession(newSeconds);
      const [active, frozen] = StreamThrottle.calculateSessionsSeconds(newSeconds);
      this.activeSessionRemainingSeconds = active;
      this.frozenSessionRemainingSeconds = frozen;

      const whatHappened = StreamThrottle.whatHappened(newSeconds);
      if (whatHappened === STREAM_EVENT.FrozenSessionStarted) {
        this.webrtc.stopStream();
      } else if (whatHappened === STREAM_EVENT.CycleFinished) {
        clearInterval(this.basicStreamTimerId);
        this.remainingSeconds = StreamThrottle.defaultRemainingSeconds();
        this.streamThrottle.removeFromStorage();
      }
    }
  },

  methods: {
    onStreamAvailable() {
      this.streamStatus = STREAM_STATUS.Available
      if (this.autoplay) {
        this.webrtc.startStream()
      } else {
        if (!this.printer.basicStreamingInWebrtc()) {
          return
        }
        const remainingSeconds = this.streamThrottle.restoreRemainingSeconds();
        this.remainingSeconds = remainingSeconds;
        const currSession = StreamThrottle.currentSession(remainingSeconds);
        if (currSession === STREAM_SESSION.Frozen) {
          this.basicStreamTimerId = setInterval(() => this.remainingSeconds -= 1, 1000);
        } else if (currSession === STREAM_SESSION.Active) {
          this.startActiveSession();
        }
      }
    },
    startActiveSession() {
      this.webrtc.startStream();
    },
    onWebRTCRemoteStream(stream) {
      Janus.attachMediaStream(this.$refs.video, stream)
      const videoTracks = stream.getVideoTracks()
      if (videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
        return
      }
      this.streamStatus = STREAM_STATUS.Started
    },
    onLoadStart() {
      this.isVideoLoading = true
    },
    onCanPlay() {
      this.isVideoLoading = false
      if (!this.autoplay) {
        this.basicStreamTimerId = setInterval(() => this.remainingSeconds -= 1, 1000);
        this.streamThrottle.saveToStorage(this.remainingSeconds);
      }
    },
    onWebRTCCleanup() {
      this.streamStatus = STREAM_STATUS.Available
    },

    onInfoClicked() {
      if (this.autoplay) {
        return
      }
      this.$swal.Prompt.fire({
        title: 'Upgrade for Better Streaming',
        html: `
          <p>Because you are now on the <a target="_blank" href="https://www.obico.io/docs/user-guides/upgrade-to-pro/?source=basic_streaming">Obico Cloud Free plan</a>:</p>
          <ul>
            <li>Streaming is limited to 5 FPS (frames per second).</li>
            <li>After 30 seconds of streaming there is a 30-second cooldown before you can resume streaming.</li>
          </ul>
          <p>Support the Obico project by <a href="https://app.obico.io/ent_pub/pricing/?source=basic_streaming">upgrading to the Pro plan for little more than 1 Starbucks a month.</a></p> The Pro plan offers many perks, including the <a target="_blank" href="https://www.obico.io/docs/user-guides/webcam-streaming-for-human-eyes/?source=basic_streaming">Premium Streaming</a>:</p>
          <ul>
            <li>Smooth 25 FPS.</li>
            <li>Unlimited streaming with no cooldowns.</li>
          </ul>
        `,
        showCloseButton: true,
      })
    },

    // Slow link
    fixSlowLinkTextWidth() {
      const width = window.getComputedStyle(this.$refs.slowLinkText).width
      this.$refs.slowLinkText.style.width = width
    },
    onSlowLink(loss) {
      this.slowLinkLoss += loss
    },
    onSlowLinkClick() {
      this.isSlowLinkShowing = false
      this.isSlowLinkHiding = false
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

    // Track muted (buffering)
    onMutedStatusClick() {
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
  },

  unmounted() {
    if (this.basicStreamTimerId) {
      clearInterval(this.basicStreamTimerId);
    }
  },
}
</script>

<style lang="sass" scoped>
.centered-element
  position: absolute
  width: 3rem
  height: 3rem
  top: calc(50% - 1.5rem)
  left: calc(50% - 1.5rem)
  z-index: 99

.overlay-info
  position: absolute
  right: 0
  top: 0
  z-index: 99
  background-color: rgb(0 0 0 / .5)
  padding: 4px 8px

.streaming-info
  text-align: right
  &.clickable
    cursor: pointer

.streaming-guide
  left: 0
  display: flex
  justify-content: space-between
  cursor: pointer

  @media (max-width: 576px)
    font-size: .8rem

  &:hover .learn-more
    color: var(--color-primary-hover)

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
