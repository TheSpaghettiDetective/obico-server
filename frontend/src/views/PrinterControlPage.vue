<template>
  <page-layout>
    <template #topBarRight>
      <div class="action-panel"></div>
    </template>
    <template #content>
      <loading-placeholder v-if="!printer" />
      <div v-else class="page-container" fluid>
        <div class="widgets-container">
          <div class="widget"></div>
          <div class="widget"></div>
          <div class="widget"></div>
          <div class="widget"></div>
          <div class="widget"></div>
        </div>
        <div class="stream-container">
          <div v-if="currentBitrate" class="streaming-info overlay-info small">
            {{ currentBitrate }}
          </div>
          <div ref="streamInner" class="stream-inner">
            <streaming-box
              :printer="printer"
              :webrtc="webrtc"
              :autoplay="user.is_pro"
              :show-bitrate="false"
              @onBitrateUpdated="onBitrateUpdated"
            />
          </div>
        </div>
      </div>
    </template>
  </page-layout>
</template>

<script>
import split from 'lodash/split'
import urls from '@config/server-urls'
import { normalizedPrinter } from '@src/lib/normalizers'
import StreamingBox from '@src/components/StreamingBox'
import PrinterComm from '@src/lib/printer-comm'
import WebRTCConnection from '@src/lib/webrtc'
import PageLayout from '@src/components/PageLayout.vue'
import { isLocalStorageSupported } from '@static/js/utils'
import { user } from '@src/lib/page-context'

const AXIS = {
  x: 'x',
  y: 'y',
  z: 'z',
  xy: ['x', 'y'],
}

const DIRECTIONS = {
  up: 1,
  down: -1,
  home: 0,
}

export default {
  name: 'PrinterControlPage',

  components: {
    StreamingBox,
    PageLayout,
  },

  data() {
    return {
      axis: AXIS,
      directions: DIRECTIONS,

      user: null,
      printerId: null,
      printer: null,
      webrtc: null,
      currentBitrate: null,

      // Current distance and possible options
      jogDistance: 10,
      jogDistanceOptions: [0.1, 1, 10, 100],
    }
  },

  watch: {
    jogDistance: function (newValue) {
      if (isLocalStorageSupported()) {
        localStorage.setItem(`mm-per-step-${this.printerId}`, newValue)
      }
    },
    printer: function (newValue, oldValue) {
      if (newValue && oldValue === null) {
        this.$nextTick(this.resizeStream)
      }
    },
  },

  created() {
    this.user = user()
    this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()

    // Get jogDistance from localStorage or set default value
    const storageValue = isLocalStorageSupported()
      ? localStorage.getItem(`mm-per-step-${this.printerId}`)
      : null
    this.jogDistance = storageValue ? storageValue : this.jogDistance

    this.webrtc = WebRTCConnection()

    this.printerComm = PrinterComm(
      this.printerId,
      urls.printerWebSocket(this.printerId),
      (data) => {
        this.printer = normalizedPrinter(data, this.printer)
        if (this.webrtc && !this.webrtc.initialized) {
          this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
          this.printerComm.setWebRTC(this.webrtc)
        }
      }
    )
    this.printerComm.connect()
  },

  mounted() {
    document.querySelector('body').style.paddingBottom = 0
    addEventListener('resize', this.resizeStream)
  },

  methods: {
    onBitrateUpdated(bitrate) {
      this.currentBitrate = bitrate.value
    },
    resizeStream() {
      const streamInner = this.$refs.streamInner
      if (!streamInner) return
      const streamContainer = streamInner.parentElement

      const style = window.getComputedStyle(streamContainer)
      const position = style.getPropertyValue('position')
      if (position !== 'fixed') {
        streamInner.style.width = '100%'
        streamInner.style.height = 'auto'
        return
      }

      const streamContainerRect = streamContainer.getBoundingClientRect()
      const streamContainerWidth = streamContainerRect.width
      const streamContainerHeight = streamContainerRect.height

      const isVertical = this.printer.settings.webcam_rotate90
      const isRatio169 = false
      const multiplier = isRatio169 ? (isVertical ? 16 / 9 : 9 / 16) : isVertical ? 4 / 3 : 3 / 4

      // 1. calc width as 100% of parent
      let innerWidth = streamContainerWidth

      // 2. calc height based on width, ratio and rotation
      let innerHeight = innerWidth * multiplier

      // 3. if height is bigger than parent height, calc height as 100% of parent
      if (innerHeight > streamContainerHeight) {
        innerHeight = streamContainerHeight
        innerWidth = innerHeight / multiplier
      }

      // hack to make StreamBox fit container
      if (isVertical) {
        innerWidth = Math.max(innerWidth, innerHeight)
        innerHeight = Math.max(innerWidth, innerHeight)
      }

      streamInner.style.width = innerWidth + 'px'
      streamInner.style.height = innerHeight + 'px'
    },
    // Control request after button click
    control(axis, direction) {
      let args = []
      let func = 'jog'

      if (direction === this.directions.home) {
        args.push(axis)
        func = 'home'
      } else {
        args.push({ [axis]: direction * this.jogDistance })
      }

      const payload = { func: func, target: '_printer', args: args }
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (ret?.error) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: ret.error,
          })
        }
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.page-container
  --widget-width: 480px
  display: flex
  flex: 1
  padding: 0 15px

.widgets-container
  flex-shrink: 0
  width: var(--widget-width)

  .widget
    background-color: var(--color-surface-secondary)
    border-radius: var(--border-radius-md)
    margin-bottom: 15px
    height: 240px
    &:last-of-type
      margin-bottom: 0

.stream-container
  flex: 1
  position: fixed
  right: var(--gap-between-blocks)
  top: calc(50px + var(--gap-between-blocks))
  height: calc(100vh - 50px - var(--gap-between-blocks)*2)
  width: calc(100vw - 100px - var(--gap-between-blocks)*3 - var(--widget-width))
  background-color: #000
  border-radius: var(--border-radius-md)
  overflow: hidden

  .stream-inner
    position: absolute
    top: 50%
    left: 50%
    transform: translate(-50%, -50%)

@media (max-width: 1024px)
  .page-container
    width: 100%
    max-width: var(--widget-width)
    margin: 0 auto
    flex-direction: column

  .widgets-container
    order: 2
    width: 100%

  .stream-container
    order: 1
    position: relative
    top: 0
    left: 0
    width: 100%
    margin-bottom: 15px

    .stream-inner
      position: static
      transform: none

.page-container
  @media (max-width: 510px)
    padding: 0 15px

    .widgets-container
      width: 100%

.streaming-info
  text-align: right
.overlay-info
  position: absolute
  right: 0
  top: 0
  z-index: 99
  background-color: rgb(0 0 0 / .5)
  padding: 4px 8px
</style>
