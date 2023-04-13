<template>
  <page-layout>
    <template #topBarLeft>
      <div class="back-btn d-none d-md-block">
        <b-button variant="link" class="ghost" href="/printers/">
          <i class="fa-solid fa-angle-left"></i>&nbsp; Back
        </b-button>
      </div>
      <span class="divider d-none d-md-block"></span>
      <div class="printer-name truncated">
        {{ printer ? printer.name : '' }}
      </div>
    </template>

    <template #topBarRight>
      <div v-if="printer" class="action-panel">
        <!-- Tunnel -->
        <a
          :href="`/tunnels/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="OctoPrint Tunnel"
        >
          <svg class="custom-svg-icon">
            <use href="#svg-octoprint-tunneling" />
          </svg>
          <span class="sr-only">OctoPrint Tunnel</span>
        </a>
        <!-- Configure -->
        <a
          :href="`/printers/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="Configure"
        >
          <i class="fa-solid fa-wrench"></i>
          <span class="sr-only">Configure</span>
        </a>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="[
              {
                key: 'tunnel',
                svgIcon: 'svg-octoprint-tunneling',
                title: 'OctoPrint Tunnel',
                href: `/tunnels/${printer.id}/`,
              },
              {
                key: 'settings',
                icon: 'fa-solid fa-wrench',
                title: 'Configure',
                href: `/printers/${printer.id}/`,
              },
            ]"
          />
        </b-dropdown>
      </div>
    </template>
    <template #content>
      <loading-placeholder v-if="!printer" />
      <div v-else class="page-container" fluid>
        <div class="widgets-container">
          <printer-actions-widget
            :printer="printer"
            @PrinterActionConnectClicked="onPrinterActionConnectClicked"
            @PrinterActionPauseClicked="onPrinterActionPauseClicked"
            @PrinterActionResumeClicked="onPrinterActionResumeClicked($event)"
            @PrinterActionCancelClicked="onPrinterActionCancelClicked"
          />
          <print-progress-widget
            v-if="!printer.isOffline() && !printer.isDisconnected()"
            ref="printProgressWidget"
            :printer="printer"
            :print="lastPrint"
            :is-print-starting="isPrintStarting"
            @PrintActionRepeatClicked="onPrintActionRepeatClicked"
          />
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
import axios from 'axios'
import { normalizedPrinter, normalizedPrint } from '@src/lib/normalizers'
import StreamingBox from '@src/components/StreamingBox'
import PrinterComm from '@src/lib/printer-comm'
import WebRTCConnection from '@src/lib/webrtc'
import PageLayout from '@src/components/PageLayout.vue'
import { isLocalStorageSupported } from '@static/js/utils'
import { user } from '@src/lib/page-context'
import CascadedDropdown from '@src/components/CascadedDropdown'
import PrinterActionsWidget from '@src/components/printer-control/PrinterActionsWidget'
import PrintProgressWidget from '@src/components/printer-control/PrintProgressWidget'
import ConnectPrinter from '@src/components/printers/ConnectPrinter.vue'
import { sendToPrint } from '@src/components/g-codes/sendToPrint'

const PAUSE_PRINT = '/pause_print/'
const RESUME_PRINT = '/resume_print/'
const CANCEL_PRINT = '/cancel_print/'

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
    CascadedDropdown,
    PrinterActionsWidget,
    PrintProgressWidget,
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
      lastPrint: null,
      isPrintStarting: false,
      lastPrintFetchCounter: 0,

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
    printer: {
      handler(newValue, oldValue) {
        if (newValue && oldValue === null) {
          this.$nextTick(this.resizeStream)
        } else {
          if (newValue?.isActive() !== oldValue?.isActive()) {
            // poll server for the last print with correct status on starting/cancelling/finishing print
            this.fetchLastPrint({ pollForCorrect: true })
          }
        }
      },
      deep: true,
    },
  },

  created() {
    this.user = user()
    this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    this.fetchLastPrint()

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
        if (this.$refs.printProgressWidget) {
          this.$refs.printProgressWidget.updateState()
        }
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
    fetchLastPrint(props) {
      const defaultProps = { pollForCorrect: false }
      const { pollForCorrect } = props || defaultProps

      axios
        .get(urls.prints(), {
          params: {
            start: 0,
            limit: 1,
            filter_by_printer_ids: [this.printerId],
            sorting: 'date_desc',
          },
        })
        .then((response) => {
          if (response.data.length) {
            this.lastPrint = normalizedPrint(response.data[0])

            if (pollForCorrect) {
              let retry = false
              if (this.printer.isActive() !== this.lastPrint.status.isActive) {
                retry = true
              }

              if (retry && this.lastPrintFetchCounter < 5) {
                const newDelay = (this.lastPrintFetchCounter + 1) * 1000
                setTimeout(() => this.fetchLastPrint({ pollForCorrect: true }), newDelay)
                this.lastPrintFetchCounter += 1
              } else {
                this.lastPrintFetchCounter = 0
              }
            }
          }
        })
        .catch((error) => {
          console.error('Error fetching last print: ', error)
        })
    },
    sendPrinterAction(printerId, path, isOctoPrintCommand) {
      axios.post(urls.printerAction(printerId, path)).then(() => {
        let toastHtml = ''
        if (isOctoPrintCommand) {
          toastHtml +=
            `<h6>Successfully sent command to ${this.printer.name}!</h6>` +
            '<p>It may take a while to be executed.</p>'
        }
        if (toastHtml != '') {
          this.$swal.Toast.fire({
            icon: 'success',
            html: toastHtml,
          })
        }
      })
    },
    onPrinterActionPauseClicked() {
      this.$swal.Confirm.fire({
        html: 'If you haven\'t changed the default configuration, the heaters will be turned off, and the print head will be z-lifted. The reversed will be performed before the print is resumed. <a target="_blank" href="https://www.obico.io/docs/user-guides/detection-print-job-settings#when-print-is-paused">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a>',
      }).then((result) => {
        if (result.value) {
          this.sendPrinterAction(this.printer.id, PAUSE_PRINT, true)
        }
      })
    },
    onPrinterActionResumeClicked(ev) {
      if (this.printer.alertUnacknowledged()) {
        this.onNotAFailureClicked(ev, true)
      } else {
        this.sendPrinterAction(this.printer.id, RESUME_PRINT, true)
      }
    },
    onPrinterActionCancelClicked() {
      this.$swal.Confirm.fire({
        text: 'Once cancelled, the print can no longer be resumed.',
      }).then((result) => {
        if (result.value) {
          // When it is confirmed
          this.sendPrinterAction(this.printer.id, CANCEL_PRINT, true)
        }
      })
    },
    onPrintActionRepeatClicked() {
      if (!this.lastPrint) {
        console.error("Can't repeat last print: no last print")
        return
      }
      if (this.lastPrint.g_code_file.deleted) {
        console.error("Can't repeat last print: G-Code deleted")
        return
      }
      if (!this.lastPrint.g_code_file.url) {
        // Usually OctoPrint/Klipper files
        console.error("Can't repeat last print: no G-Code file in storage")
        return
      }

      this.isPrintStarting = true

      sendToPrint({
        printerId: this.printer.id,
        gcode: this.lastPrint.g_code_file,
        isCloud: true,
        isAgentMoonraker: this.printer.isAgentMoonraker(),
        Swal: this.$swal,
        onPrinterStatusChanged: () => {
          this.isPrintStarting = false
        },
      })
    },
    onPrinterActionConnectClicked() {
      this.printerComm.passThruToPrinter(
        { func: 'get_connection_options', target: '_printer' },
        (err, connectionOptions) => {
          if (err) {
            this.$swal.Toast.fire({
              icon: 'error',
              title: 'Failed to connect!',
            })
          } else {
            if (connectionOptions.ports.length < 1) {
              this.$swal.Toast.fire({
                icon: 'error',
                title: 'Uh-Oh. No printer is found on the serial port.',
              })
            } else {
              this.$swal
                .openModalWithComponent(
                  ConnectPrinter,
                  {
                    connectionOptions: connectionOptions,
                  },
                  {
                    confirmButtonText: 'Connect',
                    showCancelButton: true,
                    preConfirm: () => {
                      return {
                        port: document.getElementById('connect-port').value,
                        baudrate: document.getElementById('connect-baudrate').value,
                      }
                    },
                  }
                )
                .then((result) => {
                  if (result.value) {
                    let args = [result.value.port, result.value.baudrate]
                    this.printerComm.passThruToPrinter({
                      func: 'connect',
                      target: '_printer',
                      args: args,
                    })
                  }
                })
            }
          }
        }
      )
    },
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
// Navbar
.printer-name
  font-size: 1rem
  max-width: 360px
  font-weight: bold
  @media (max-width: 768px)
    max-width: 200px
.divider
  margin-right: 1rem
  width: 1px
  height: 1rem
  display: inline-block
  background-color: var(--color-divider)
.custom-svg-icon
  height: 1.125rem
  width: 1.125rem

.page-container
  --widget-width: 480px
  display: flex
  flex: 1
  padding: 0 15px
  @media (max-width: 768px)
    flex: unset

.widgets-container
  flex-shrink: 0
  width: var(--widget-width)
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
