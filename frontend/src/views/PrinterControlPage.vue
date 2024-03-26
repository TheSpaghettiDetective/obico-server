<template>
  <page-layout>
    <template #topBarLeft>
      <div class="printer-name truncated">
        {{ printer ? printer.name : '' }}
      </div>
    </template>

    <template #topBarRight>
      <div v-if="printer" class="action-panel">
        <!-- Share Feed -->
        <a
          href="#"
          class="btn shadow-none action-btn icon-btn"
          title="Share"
          @click.prevent="onSharePrinter()"
        >
          <i class="fas fa-share-alt fa-lg"></i>
          <span class="sr-only">{{ $t("Share") }}</span>
        </a>
        <!-- Tunnel -->
        <a
          :href="`/tunnels/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="OctoPrint Tunnel"
        >
          <svg class="custom-svg-icon">
            <use href="#svg-tunnel" />
          </svg>
          <span class="sr-only">{{ $t("OctoPrint Tunnel") }}</span>
        </a>
        <!-- Configure -->
        <a
          :href="`/printers/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="Configure"
        >
          <i class="fas fa-wrench"></i>
          <span class="sr-only">{{ $t("Configure") }}</span>
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
                key: 'share',
                icon: 'fas fa-share-alt fa-lg',
                title: $t('Share'),
                callback: true,
              },
              {
                key: 'tunnel',
                svgIcon: 'svg-tunnel',
                title: $t('OctoPrint Tunnel'),
                href: `/tunnels/${printer.id}/`,
              },
              {
                key: 'settings',
                icon: 'fas fa-wrench',
                title: $t('Configure'),
                href: `/printers/${printer.id}/`,
              },
            ]"
            @menuOptionClicked="onMenuOptionClicked"
          />
        </b-dropdown>
      </div>
    </template>
    <template #content>
      <loading-placeholder v-if="!printer" />
      <div v-else class="page-container" fluid>
        <div class="widgets-container">
          <template v-for="widget in widgets">
            <component
              :is="widget.component"
              v-if="
                widget.enabled &&
                ((!printer.isOffline() && !printer.isDisconnected()) ||
                  widget.component === 'PrintJobControlWidget')
              "
              :key="widget.id"
              :printer="printer"
              :printer-comm="printerComm"
              :print="lastPrint"
              @sendPrinterAction="onSendPrinterAction"
              @notAFailureClicked="onNotAFailureClicked"
              @updateSettings="onUpdateSettings"
            ></component>
          </template>

          <div class="extra-actions">
            <h2 class="section-title">{{ $t("Additional Actions") }}</h2>
            <b-button variant="outline-secondary" class="custom-button" @click="onReorderClicked">
              <i class="fas fa-arrows-alt-v"></i>
              {{$t("Reorder")}} &amp; {{$t("Hide")}}
            </b-button>
            <div class="text-muted extra-actions-explanation">
              <small>{{ $t("Customize this page for each of your printers by reodering or hiding cards above.") }}</small
              >
            </div>
            <b-button variant="outline-primary" class="custom-button" href="/printers/wizard/">
              <i class="fas fa-plus"></i>
              {{$t("Add Printer")}}
            </b-button>
            <div class="text-muted extra-actions-explanation">
              <small>{{ $t("Link another printer to {brandName}.",{brandName:$t('brand_name')}) }}</small>
            </div>
          </div>
        </div>
        <div class="stream-container">
          <div ref="streamInner" class="stream-inner">
            <streaming-box
              :printer="printer"
              :webrtc="webrtc"
              :autoplay="user.is_pro"
              @onRotateRightClicked="
                (val) => {
                  customRotationDeg = val
                }
              "
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
import { isLocalStorageSupported } from '@static/js/utils'
import { normalizedPrinter, normalizedPrint } from '@src/lib/normalizers'
import StreamingBox from '@src/components/StreamingBox'
import { printerCommManager } from '@src/lib/printer-comm'
import WebRTCConnection from '@src/lib/webrtc'
import PageLayout from '@src/components/PageLayout.vue'
import { user } from '@src/lib/page-context'
import CascadedDropdown from '@src/components/CascadedDropdown'
import PrintJobControlWidget from '@src/components/printer-control/PrintJobControlWidget'
import PrintProgressWidget from '@src/components/printer-control/PrintProgressWidget'
import FailureDetectionWidget from '@src/components/printer-control/FailureDetectionWidget'
import TemperatureWidget from '@src/components/printer-control/TemperatureWidget'
import PrinterControlWidget from '@src/components/printer-control/PrinterControlWidget'
import ReorderModal from '@src/components/ReorderModal'
import { getLocalPref } from '@src/lib/pref'
import SharePrinter from '@src/components/printers/SharePrinter.vue'
import TerminalWidget from '../components/printer-control/TerminalWidget.vue'

const RESUME_PRINT = '/resume_print/'
const MUTE_CURRENT_PRINT = '/mute_current_print/?mute_alert=true'
const ACK_ALERT_NOT_FAILED = '/acknowledge_alert/?alert_overwrite=NOT_FAILED'

// Widgets config (for local storage and params) format: [{id: 1, enabled: true}, ...]
// WIDGETS below maps IDs to other useful info
const WIDGETS = [
  {
    id: 1,
    title: 'Print Job Control',
    component: 'PrintJobControlWidget',
  },
  {
    id: 2,
    title: 'Last Print / Progress',
    component: 'PrintProgressWidget',
  },
  {
    id: 3,
    title: 'Failure Detection',
    component: 'FailureDetectionWidget',
  },
  {
    id: 4,
    title: 'Temperature Controls',
    component: 'TemperatureWidget',
  },
  {
    id: 5,
    title: 'Printer Controls',
    component: 'PrinterControlWidget',
  },
  {
    id: 6,
    title: 'Terminal Widget',
    component: 'TerminalWidget',
  },
]

export default {
  name: 'PrinterControlPage',

  components: {
    StreamingBox,
    PageLayout,
    CascadedDropdown,
    PrintJobControlWidget,
    PrintProgressWidget,
    FailureDetectionWidget,
    TemperatureWidget,
    PrinterControlWidget,
    TerminalWidget,
  },

  data() {
    return {
      user: null,
      printerId: null,
      printer: null,
      webrtc: null,
      currentBitrate: null,
      lastPrint: null,
      lastPrintFetchCounter: 0,
      widgetsConfig: null,
      customRotationDeg: getLocalPref('webcamRotationDeg', 0),
    }
  },

  computed: {
    widgets() {
      if (!this.widgetsConfig) return
      return this.widgetsConfig.map((widget) => {
        const configItem = WIDGETS.find((w) => w.id === widget.id)
        return { ...widget, ...configItem }
      })
    },
    videoRotationDeg() {
      const rotation = +(this.printer?.settings?.webcam_rotation ?? 0) + this.customRotationDeg
      return rotation % 360
    },
  },

  watch: {
    printer: {
      handler(newValue, oldValue) {
        if (newValue && oldValue === null) {
          this.$nextTick(this.resizeStream)
          this.widgetsConfig = this.restoreWidgets()
        } else {
          if (
            newValue?.isActive() !== oldValue?.isActive() ||
            newValue?.current_print?.started_at !== oldValue?.current_print?.started_at
          ) {
            // poll server for the last print with correct status on starting/cancelling/finishing print
            this.fetchLastPrint({ pollForCorrect: true })
          }
        }
      },
      deep: true,
    },
    videoRotationDeg() {
      this.resizeStream()
    },
  },

  created() {
    this.user = user()
    this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    this.fetchLastPrint()

    this.webrtc = WebRTCConnection()

    this.printerComm = printerCommManager.getOrCreatePrinterComm(
      this.printerId,
      urls.printerWebSocket(this.printerId),
      {
        onPrinterUpdateReceived: (data) => {
          this.printer = normalizedPrinter(data, this.printer)
          if (this.webrtc && !this.webrtc.initialized) {
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)
          }
        },
      }
    )
    this.printerComm.connect()
  },

  mounted() {
    document.querySelector('body').style.paddingBottom = 0
    addEventListener('resize', this.resizeStream)
  },

  methods: {
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'share') {
        this.onSharePrinter()
      }
    },
    onSharePrinter() {
      this.$swal.openModalWithComponent(
        SharePrinter,
        {
          isProAccount: this.user.is_pro,
          printer: this.printer,
        },
        {
          confirmButtonText: 'Close',
        }
      )
    },
    restoreWidgets() {
      let widgets = WIDGETS.map((w) => ({ id: w.id, enabled: true }))

      if (isLocalStorageSupported()) {
        widgets =
          JSON.parse(localStorage.getItem('printer-control-widgets-' + this.printer.id)) || widgets
      }

      // add any new widgets
      for (const WIDGET of WIDGETS) {
        if (!widgets.find((w) => w.id === WIDGET.id)) {
          widgets.push({ id: WIDGET.id, enabled: true })
        }
      }

      // remove any old widgets which are no longer supported
      for (const widget of widgets) {
        if (!WIDGETS.find((w) => w.id === widget.id)) {
          widgets.splice(widgets.indexOf(widget), 1)
        }
      }

      // delete terminal widget if it's not supported
      const terminalWidget = widgets.find((w) => w.id === 6)
      if (terminalWidget && !this.printer.isAgentVersionGte('2.3.11', '1.4.4')) {
        widgets.splice(widgets.indexOf(terminalWidget), 1)
      }

      if (isLocalStorageSupported()) {
        localStorage.setItem('printer-control-widgets-' + this.printer.id, JSON.stringify(widgets))
      }
      return widgets
    },
    onUpdateSettings(props) {
      const { settingName, settingValue } = props
      this.printer[settingName] = settingValue

      axios
        .patch(urls.printer(this.printer.id), {
          [settingName]: settingValue,
        })
        .catch((err) => {
          console.error('Failed to update printer settings: ', err)
        })
    },
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
          }

          if (pollForCorrect) {
            let retry = false
            if (!this.lastPrint || this.printer.isActive() !== this.lastPrint.status.isActive) {
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
        })
        .catch((error) => {
          console.error('Error fetching last print: ', error)
        })
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

      const isVertical = this.videoRotationDeg % 180 !== 0
      const isRatio169 = this.printer.settings.ratio169
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
    onNotAFailureClicked(ev, resumePrint) {
      this.$swal.Confirm.fire({
        title: `${this.$i18next.t('Noted!')}`,
        html: `<p>${this.$i18next.t("Do you want to mute failure detection on for this print?")}</p><small>${this.$i18next.t("If you select 'Mute', failure detection will be turned off for this print, but will be automatically turned on for your next print.")}</small>`,
        confirmButtonText: `${this.$i18next.t('Mute')}`,
        cancelButtonText: `${this.$i18next.t('Cancel')}`,
      }).then((result) => {
        if (result.isConfirmed) {
          // Hack: So that 2 APIs are not called at the same time
          setTimeout(() => {
            this.onSendPrinterAction(this.printer.id, MUTE_CURRENT_PRINT)
          }, 1000)
        }
        if (resumePrint) {
          this.printer.setTransientState('Resuming')
          this.onSendPrinterAction(this.printer.id, RESUME_PRINT)
        } else {
          this.onSendPrinterAction(this.printer.id, ACK_ALERT_NOT_FAILED)
        }
      })
      ev.preventDefault()
    },
    onSendPrinterAction(printerId, path, isOctoPrintCommand) {
      axios.post(urls.printerAction(printerId, path))
    },
    onReorderClicked() {
      this.$swal
        .openModalWithComponent(
          ReorderModal,
          {
            items: [...this.widgetsConfig],
            extraInfo: WIDGETS,
          },
          {
            confirmButtonText: `${this.$i18next.t('Save')}`,
            showCancelButton: true,
            preConfirm: () => {
              return {
                config: document.getElementById('sorting-config').value,
              }
            },
          }
        )
        .then((result) => {
          if (result.value?.config) {
            const config = JSON.parse(result.value.config)

            this.widgetsConfig = config

            if (isLocalStorageSupported()) {
              localStorage.setItem(
                'printer-control-widgets-' + this.printer.id,
                JSON.stringify(config)
              )
            }
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
  height: 1.25rem
  width: 1.25rem

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
    box-sizing: content-box
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
    flex: 0

    .stream-inner
      position: static
      transform: none

.page-container
  @media (max-width: 510px)
    box-sizing: border-box
    padding: 0 15px

    .widgets-container
      width: 100%

.extra-actions
  display: flex
  justify-content: center
  margin-top: var(--gap-between-blocks)
  gap: 1rem
  .extra-actions-explanation, .section-title
    display: none
  @media (max-width: 510px)
    margin-top: 2rem
    flex-direction: column
    .extra-actions-explanation
      display: block
      text-align: center
      margin-top: -0.5rem
      margin-bottom: 1rem
    .section-title
      display: block
      text-align: center
      margin-bottom: 1rem
</style>
