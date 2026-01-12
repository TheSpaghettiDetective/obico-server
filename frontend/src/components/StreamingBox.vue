<template>
  <div>
    <div
      v-show="slowLinkLoss > 50"
      ref="slowLinkWrapper"
      class="slow-link-wrapper"
      @click="slowLinkClicked"
      @mouseenter="
        fixSlowLinkTextWidth()
        slowLinkShowing = true
        slowLinkHiding = false
      "
      @mouseleave="
        fixSlowLinkTextWidth()
        slowLinkShowing = false
        slowLinkHiding = true
      "
    >
      <div class="icon bg-warning">
        <i class="fas fa-exclamation"></i>
      </div>
      <div
        ref="slowLinkText"
        class="text"
        :class="{
          'show-and-hide': !slowLinkShowing && !slowLinkHiding,
          showing: slowLinkShowing && !slowLinkHiding,
          hiding: !slowLinkShowing && slowLinkHiding,
        }"
      >
        {{$t("Video frames dropped")}}
      </div>
    </div>
    <div v-show="trackMuted" class="muted-status-wrapper">
      <div class="text">{{ $t("Buffering...") }}</div>
      <a href="#" @click="showMutedStatusDescription($event)">{{ $t("Why is it stuck?") }}</a>
    </div>
    <b-button
      v-if="
        isVideoAvailable && !autoplay && (isBasicStreamingReadyToPlay || isBasicStreamingFrozen)
      "
      class="centered-element p-0"
      :disabled="isBasicStreamingFrozen"
      @click="onPlayBtnClicked"
    >
      <i v-if="isBasicStreamingReadyToPlay" class="fas fa-play ml-1"></i>
      <span v-if="isBasicStreamingFrozen" class="medium"
        >{{ remainingSecondsUntilNextCycle }}s</span
      >
    </b-button>
    <b-spinner
      v-if="trackMuted || videoLoading"
      class="centered-element"
      label="Buffering..."
    ></b-spinner>
    <div v-if="taggedSrc && !showMJpeg && !showVideo" class="streaming-info overlay-info small">
      {{$t("Real-time stream unavailable, showing last captured image")}}
    </div>
    <div v-if="isVideoAvailable">
      <!-- show countdown and bitrate while streaming -->
      <div
        v-if="(!autoplay && isBasicStreamingInProgress) || currentBitrate"
        class="streaming-info overlay-info small"
        :class="{ clickable: isBasicStreamingInProgress }"
        @click="onInfoClicked"
      >
        <div v-if="isBasicStreamingInProgress" class="text-success">
          {{ remainingSecondsCurrentVideoCycle }}
        </div>
        <div v-if="currentBitrate">{{ currentBitrate }}</div>
      </div>
      <!-- show full-width info message -->
      <div
        v-if="!autoplay && (isBasicStreamingReadyToPlay || isBasicStreamingFrozen)"
        class="streaming-guide overlay-info"
        @click="onInfoClicked"
      >
        <div v-if="isBasicStreamingReadyToPlay" class="message">
          {{$t("Webcam streams up to 5 FPS for Free")}}
        </div>
        <div v-if="isBasicStreamingFrozen" class="message text-warning">
          {{ remainingSecondsUntilNextCycle }}s left in the cooldown period
        </div>
        <a href="#" class="learn-more">{{ $t("Learn more...") }}</a>
      </div>
    </div>
    <div class="image-container">
      <img
        class="webcamImage"
        :style="webcamStyle"
        :src="require('@static/img/print-padded.png')"
      />
      <img
        v-if="taggedSrc"
        class="webcamImage stackedImage"
        :style="webcamStyle"
        :src="taggedSrc"
        :alt="printer.name + ' current image'"
      />
      <img
        :src="mjpgSrc"
        v-show="showMJpeg"
        class="webcamImage stackedImage"
        :style="webcamStyle"
      />
      <video
        v-show="showVideo"
        ref="video"
        class="webcamImage stackedImage"
        :style="webcamStyle"
        :poster="taggedSrc"
        autoplay
        muted
        playsinline
        @loadstart="onLoadStart()"
        @canplay="onCanPlay()"
      >
      </video>
    </div>

    <div class="extra-controls">
      <div
        v-if="showVideo || showVideo || taggedSrc"
        class="video-control-btn"
        @click="onRotateRightClicked"
      >
        <font-awesome-icon icon="fa-solid fa-rotate-right" />
      </div>
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'
import ifvisible from 'ifvisible'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import Janus from '@src/lib/janus'
import { toArrayBuffer } from '@src/lib/utils'
import ViewingThrottle from '@src/lib/viewing-throttle'

function MJpegStreamDecoder(onFrame) {
  const self = {
    onFrame,
    contentLength: NaN,
    imageBuffer: '',
    bytesRead: 0,
    originalJpgLength: 0,
  }

  self.onMJpegChunk = function (maybeBin) {
    toArrayBuffer(maybeBin, (arrayBuffer) => {
      const value = new TextDecoder('utf-8').decode(new Uint8Array(arrayBuffer))
      if (self.contentLength) {
        self.imageBuffer += value
        self.bytesRead += value.length

        if (self.bytesRead >= self.contentLength) {
          const jpg = self.imageBuffer
          const jpgLength = self.originalJpgLength
          self.contentLength = NaN
          self.imageBuffer = ''
          self.bytesRead = 0
          self.originalJpgLength = 0
          self.onFrame(jpg, jpgLength)
        }
      } else {
        if (value.slice(0, 2) == '\r\n' && value.slice(value.length - 2) == '\r\n') {
          // if (isEqual(value.slice(0, 2), crlf) && isEqual(value.slice(value.byteLength-2), crlf) ) {
          // const lengthHeaders = (new TextDecoder("utf-8")).decode( value.slice(2, value.byteLength - 2) ).split(':');
          const lengthHeaders = value.slice(2, value.length - 2).split(':')
          self.contentLength = parseInt(lengthHeaders[0])
          self.originalJpgLength = parseInt(lengthHeaders[1])
        }
      }
    })
  }

  return self
}

export default {
  name: 'StreamingBox',

  props: {
    printer: {
      type: Object,
      required: true,
    },
    webrtc: {
      type: Object,
      default: null,
    },
    webcam: {
      type: Object,
      default: null,
    },
    halfHeight: {
      type: Boolean,
      default: false,
    },
    autoplay: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      stickyStreamingSrc: null,
      isVideoAvailable: false,
      isVideoVisible: false,
      remainingSecondsCurrentVideoCycle: 30,
      remainingSecondsUntilNextCycle: -1,
      currentBitrate: null,
      slowLinkLoss: 0,
      slowLinkShowing: false, // show on mousenter
      slowLinkHiding: false, // hide on moseleave
      trackMuted: false,
      videoLoading: false,
      mjpgSrc: null,
      localStorageRotationKey: `${this.printer.id}_${this.webcam?.stream_id || 0}`,
      customRotationDeg: 0,
    }
  },

  computed: {
    showVideo() {
      return this.isVideoVisible && this.stickyStreamingSrc !== 'IMAGE'
    },
    showMJpeg() {
      return this.mjpgSrc && this.stickyStreamingSrc !== 'IMAGE'
    },
    videoRotationDeg() {
      const rotation = +(this.webcam?.rotation || 0) + this.customRotationDeg
      return rotation % 360
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
      if (!this.webcam || this.webcam?.is_primary_camera) {
        return  get(this.printer, 'pic.img_url', null)
      }
      return null
    },

    // streaming timeline
    isBasicStreamingInProgress() {
      return (
        this.remainingSecondsCurrentVideoCycle > 0 && this.remainingSecondsCurrentVideoCycle < 30
      )
    },
    isBasicStreamingReadyToPlay() {
      return (
        !this.isVideoVisible &&
        !this.trackMuted &&
        !this.videoLoading &&
        (this.remainingSecondsCurrentVideoCycle == 30 || this.remainingSecondsUntilNextCycle == 0)
      )
    },
    isBasicStreamingFrozen() {
      return this.remainingSecondsUntilNextCycle > 0 && !this.isVideoVisible
    },
    basicStreamingInWebrtc() {
      return this.printer.isAgentVersionGte('2.1.0', '0.3.0')
    },
    webcamStyle() {
      const maxHeight = window.innerHeight / (this.halfHeight ? 2 : 1) - 75
      const output = {
          transform: this.generateTransform(
              this.webcam?.flipH ?? false,
              this.webcam?.flipV ?? false,
              this.videoRotationDeg ?? 0
          ),
          aspectRatio: 16 / 9,
          maxHeight: maxHeight + 'px',
          maxWidth: 'auto',
      }

      if (this.webcam?.streamRatio) {
          const [width, height] = this.webcam.streamRatio.split(':').map(Number)
          output.aspectRatio = width / height
          output.maxWidth = (window.innerHeight - 155) * output.aspectRatio + 'px'
      }

      if (this.webcam?.streamRatio && [90, 270].includes(this.videoRotationDeg)) {
          if (output.transform === 'none') output.transform = ''
          const scale = 1 / output.aspectRatio
          output.transform += ' rotate(' + this.videoRotationDeg + 'deg) scale(' + scale + ')'
      }

      return output
    },
  },
  watch: {
    webrtc: {
      handler: 'initWebRTC',
    },
  },
  created() {
    this.customRotationDeg = getLocalPref('webcamRotationDeg', 0, this.localStorageRotationKey)
    this.mjpegStreamDecoder = new MJpegStreamDecoder((jpg, l) => {
      this.mjpgSrc = `data:image/jpg;base64,${jpg}`
      this.onCanPlay()
    })
    if (!this.autoplay) {
      this.videoLimit = ViewingThrottle(this.printer.id, this.countDownCallback)
    }
    this.initWebRTC()
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
  },

  methods: {
    initWebRTC() {
      if (this.webrtc) {
        this.webrtc.setCallbacks({
          onStreamAvailable: this.onStreamAvailable,
          onRemoteStream: this.onWebRTCRemoteStream,
          onDefaultStreamCleanup: () => (this.isVideoVisible = false),
          onSlowLink: this.onSlowLink,
          onTrackMuted: () => (this.trackMuted = true),
          onTrackUnmuted: () => (this.trackMuted = false),
          onBitrateUpdated: (bitrate) => {
            this.currentBitrate = bitrate.value
          },
          onMJpegData: this.mjpegStreamDecoder.onMJpegChunk,
        })
      }
    },
    onRotateRightClicked() {
      this.customRotationDeg = this.customRotationDeg + 90;
      setLocalPref('webcamRotationDeg', this.customRotationDeg % 360, this.localStorageRotationKey)
      this.$emit('onRotateRightClicked', this.customRotationDeg);
    },
    onCanPlay() {
      this.videoLoading = false
      if (!this.autoplay) {
        this.videoLimit.startOrResumeVideoCycle()
      }
    },
    onLoadStart() {
      this.videoLoading = true
    },
    onStreamAvailable(webrtcConn) {
      if (this.autoplay) {
        webrtcConn.startStream()
      } else {
        if (!this.basicStreamingInWebrtc) {
          return
        }
        if (!this.autoplay && this.isBasicStreamingInProgress) {
          webrtcConn.startStream()
        }
        this.videoLimit.resumeVideoCycle()
      }
      this.isVideoAvailable = true
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

    /** Free user streaming **/

    countDownCallback(remainingSecondsCurrentVideoCycle, remainingSecondsUntilNextCycle) {
      if (this.remainingSecondsCurrentVideoCycle > 0 && remainingSecondsCurrentVideoCycle <= 0) {
        this.webrtc.stopStream()
      }
      this.remainingSecondsCurrentVideoCycle = remainingSecondsCurrentVideoCycle
      this.remainingSecondsUntilNextCycle = remainingSecondsUntilNextCycle
    },

    onInfoClicked() {
  if (this.autoplay) {
    return;
  }
  this.$swal.Prompt.fire({
    title: `${this.$i18next.t(`Upgrade for Better Streaming`)}`,
    html: `
      <p>${this.$i18next.t("Because you are now on the")} <a target="_blank" href="${this.getDocUrl('/user-guides/upgrade-to-pro/?source=basic_streaming')}">${this.$i18next.t("{brandName} Cloud Free plan",{brandName:this.$syndicateText.brandName})}</a>:</p>
      <ul>
        <li>${this.$i18next.t("Streaming is limited to 5 FPS (frames per second).")}</li>
        <li>${this.$i18next.t("After 30 seconds of streaming there is a 30-second cooldown before you can resume streaming.")}</li>
      </ul>
      <p>${this.$i18next.t("Support the {brandName} project by",{brandName:this.$syndicateText.brandName})} <a href="${this.getAppUrl('/ent_pub/pricing/?source=basic_streaming')}">${this.$i18next.t("upgrading to the Pro plan for little more than 1 Starbucks a month.")}</a></p> ${this.$i18next.t("The Pro plan offers many perks, including the")} <a target="_blank" href="${this.getDocUrl('/user-guides/webcam-streaming-for-human-eyes/?source=basic_streaming')}">${this.$i18next.t("Premium Streaming")}</a>:</p>
      <ul>
        <li>${this.$i18next.t("Smooth 25 FPS.")}</li>
        <li>${this.$i18next.t("Unlimited streaming with no cooldowns.")}</li>
      </ul>
    `,
    showCloseButton: true,
      });
    },

    /** End of free user streaming **/

    /** Video warning handling */

    onPlayBtnClicked() {
      this.webrtc.startStream()
    },

    fixSlowLinkTextWidth() {
      const width = window.getComputedStyle(this.$refs.slowLinkText).width
      this.$refs.slowLinkText.style.width = width
    },

    onSlowLink(loss) {
      this.slowLinkLoss += loss
    },

    slowLinkClicked() {
      this.slowLinkShowing = false;
      this.slowLinkHiding = false;
      this.slowLinkLoss = 0;

      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Video frames dropped')}`,
        html: `
          <p>${this.$i18next.t("The video frames are getting dropped because there is most likely a bandwidth bottleneck along the route they travel from your Raspberry Pi to your computer. The bottleneck can be anywhere, but in most cases,")} <Text bold>${this.$i18next.t("it is either your computer's internet connection, or your Raspberry Pi's")}</Text>.</p>
          <p>${this.$i18next.t("Make sure your computer is connected to the same network as your Pi. If you still see this warning, you need to trouble-shoot your computer's Wi-Fi connection, probably by moving closer to the Wi-Fi router.")}</p>
          <p>${this.$i18next.t("If the webcam stream is smooth when your computer is on the same Wi-Fi network as your Pi, the bottleneck is likely with the upload speed of your internet connection. You need to run a speed test to make sure you have high-enough upload speed, as well as")} <b>${this.$i18next.t("low latency (ping)")}</b>.</p>
          <p>${this.$i18next.t("Check out")} <a target="_blank" href="${this.getDocUrl('/user-guides/webcam-feed-is-laggy/')}">${this.$i18next.t("the step-by-step trouble-shooting guide.")}</a></p>
        `,
        showCloseButton: true,
      });
    },

    showMutedStatusDescription(event) {
      event.preventDefault()

      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Webcam stream buffering')}`,
        html: `
          <p>${this.$i18next.t("When you see the messaging about webcam stream is 'buffering' occasionally, you can just reload the page. If this message repeatedly appears, it may indicate one of the problems")}:</p>
          <p class="lead">${this.$i18next.t("1. A constricted video stream on your Raspberry Pi. The most common reasons are")}:</p>
          <ul>
            <li>${this.$i18next.t("Camera resolution is set too high.")}</li>
            <li>${this.$i18next.t("Camera framerate is set too high.")}</li>
            <li>${this.$i18next.t("The upload speed of your Raspberry Pi is too low.")}</li>
          </ul>
          <p class="lead">${this.$i18next.t("2. The internet connection of your computer or phone is not fast enough.")}</p>
          <p class="lead">${this.$i18next.t("3. Your webcam is not properly connected to your Raspberry Pi.")}</p>
          <br>
          <p>${this.$i18next.t("Check")} <a target="_blank" href="${this.getDocUrl('/user-guides/webcam-feed-is-laggy')}">${this.$i18next.t("this step-by-step troubleshooting guide")}</a>.</p>
        `,
        showCloseButton: true,
      })
    },
    generateTransform(flip_horizontal, flip_vertical, rotation) {
        let transforms = ''
        if (flip_horizontal) transforms += ' scaleX(-1)'
        if (flip_vertical) transforms += ' scaleY(-1)'
        
        // Apply rotation for all degrees, not just 180
        if (rotation && rotation !== 0) {
            transforms += ` rotate(${rotation}deg)`
        }

        // return transform when exist
        if (transforms.trimStart().length) return transforms.trimStart()

        // return none as fallback
        return 'none'
    },
  },
}
</script>

<style lang="sass" scoped>
.image-container
  position: relative
  width: 100%
  height: 100%

.webcamImage
  width: 100%
  height: 100%
  object-fit: contain

.stackedImage
  position: absolute
  top: 0
  left: 0

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
  $size: 100px
  color: rgb(255 255 255 / .2)
  width: $size
  height: $size
  position: absolute
  left: calc(50% - $size / 2)
  top: calc(50% - $size / 2)

.extra-controls
  position: absolute
  display: flex
  flex-direction: row
  right: 0
  bottom: 0
  padding: .5rem
  .video-control-btn
    width: 2rem
    height: 2rem
    margin: 0.1rem
    border-radius: 999px
    background-color: var(--color-overlay)
    color: var(--color-text-secondary)
    display: flex
    align-items: center
    justify-content: center
    &:hover
      color: var(--color-text-primary)
      cursor: pointer
</style>
