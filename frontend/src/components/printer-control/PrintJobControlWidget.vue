<template>
  <widget-template :inside-card="insideCard">
    <template #title>Print Job Control</template>
    <template #content>
      <div class="wrapper">
        <div v-if="!printer.isOffline() && printer.hasError()" class="error-container">
          <div class="title">{{ printer.agentDisplayName() }} Error</div>
          <p class="text">
            {{ printer.status.state.error }}
          </p>
        </div>

        <div v-if="printer.inUserInteractionRequired()" class="warning-container">
          <p class="text">Filament Change or User Interaction Required</p>
        </div>

        <template v-if="isPrinterInTransientState">
          <b-spinner label="Processing..."></b-spinner>
          <p>{{ transientStateName }}...</p>
        </template>

        <template v-else>
          <template v-if="!printer.isOffline() && !printer.isDisconnected() && printer.isActive()">
            <p>
              <span v-if="!printer.isPaused()">Printer is Curently Printing</span>
              <span v-else>Print is Paused</span>
            </p>
            <div class="buttons">
              <b-button
                v-if="!printer.isPaused()"
                variant="warning"
                class="custom-button"
                @click="onPauseToggled($event)"
              >
                <i class="fa-solid fa-circle-pause"></i>
                Pause
              </b-button>
              <b-button
                v-else
                variant="success"
                class="custom-button"
                @click="onPauseToggled($event)"
              >
                <i class="fa-solid fa-circle-play"></i>
                Resume
              </b-button>
              <b-button variant="danger" class="custom-button" @click="onCancelClicked">
                <i class="fa-solid fa-circle-xmark"></i>
                Cancel
              </b-button>
            </div>
          </template>

          <template v-if="!printer.isOffline() && !printer.isDisconnected() && !printer.isActive()">
            <p>Open G-Code File to Start Printing</p>
            <div class="buttons">
              <b-button variant="outline-primary" class="custom-button" @click="openObicoFiles">
                <svg class="logo-small custom-svg-icon">
                  <use href="#svg-logo-compact" />
                </svg>
                Obico Files
              </b-button>
              <b-button
                v-if="printer.isAgentMoonraker()"
                variant="outline-secondary"
                class="custom-button"
                @click="openPrinterFiles"
              >
                &nbsp;
                <svg class="logo-small custom-svg-icon">
                  <use href="#svg-klipper-logo" />
                </svg>
                <svg class="logo-small custom-svg-icon">
                  <use href="#svg-fluidd-logo" />
                </svg>
                <svg class="logo-small custom-svg-icon">
                  <use href="#svg-mainsail-logo" />
                </svg>
                &nbsp;
              </b-button>
              <b-button
                v-else
                variant="outline-secondary"
                class="custom-button"
                @click="openPrinterFiles"
              >
                <svg class="logo-small custom-svg-icon">
                  <use href="#svg-octoprint-logo" />
                </svg>
                OctoPrint
              </b-button>
            </div>
          </template>
        </template>

        <template v-if="!printer.isOffline() && printer.isDisconnected()">
          <p>Printer Not Connected at the Serial Port</p>
          <div class="buttons">
            <b-button
              v-if="!printer.isAgentMoonraker()"
              variant="outline-primary"
              @click="onConnectClicked"
            >
              <i class="fa-brands fa-usb"></i> Connect
            </b-button>
          </div>
        </template>

        <template v-if="printer.isOffline()">
          <i class="fa-solid fa-triangle-exclamation big-icon warning"></i>
          <p>
            Obico for {{ printer.isAgentMoonraker() ? 'Klipper' : 'OctoPrint' }} is Offline.
            <a
              target="_blank"
              href="https://www.obico.io/docs/user-guides/troubleshoot-server-connection-issues/"
              >Why?</a
            >
          </p>
        </template>

        <b-modal v-if="printer" :id="modalId" size="lg" @hidden="resetGcodesModal">
          <g-code-file-page
            v-if="selectedGcodeId"
            :is-popup="true"
            :target-printer-id="printer.id"
            :route-params="{
              fileId: selectedGcodeId,
              printerId: printerFiles ? printer.id : null,
            }"
            :on-close="() => $bvModal.hide(modalId)"
            @goBack="
              () => {
                selectedGcodeId = null
                scrollToTop()
              }
            "
          />
          <g-code-folders-page
            v-else
            :is-popup="true"
            :target-printer="printer"
            :route-params="{
              printerId: printerFiles ? printer.id : null,
              parentFolder: null,
            }"
            :on-close="() => $bvModal.hide(modalId)"
            :saved-path="savedPath"
            :scroll-container-id="modalId"
            @openFile="
              (fileId, printerId, path) => {
                selectedGcodeId = fileId
                savedPath = path
                scrollToTop()
              }
            "
          />
        </b-modal>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import GCodeFoldersPage from '@src/views/GCodeFoldersPage.vue'
import GCodeFilePage from '@src/views/GCodeFilePage.vue'
import ConnectPrinter from '@src/components/printers/ConnectPrinter.vue'
import { setTransientState, getTransientState } from '@src/lib/printer-transient-state'

const PAUSE_PRINT = '/pause_print/'
const RESUME_PRINT = '/resume_print/'
const CANCEL_PRINT = '/cancel_print/'

export default {
  name: 'PrintJobControlWidget',

  components: {
    WidgetTemplate,
    GCodeFoldersPage,
    GCodeFilePage,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
    printerComm: {
      type: Object,
      required: true,
    },
    insideCard: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      selectedGcodeId: null,
      savedPath: [null],
      printerFiles: false,

      printerStateCheckInterval: null,
      isPrinterInTransientState: false,
      transientStateName: null,
    }
  },

  computed: {
    modalId() {
      return 'b-modal-gcodes' + this.printer.id
    },
  },

  created() {
    this.checkTransientState()
    this.printerStateCheckInterval = setInterval(this.checkTransientState, 1000)
  },

  unmounted() {
    clearInterval(this.printerStateCheckInterval)
  },

  methods: {
    openObicoFiles() {
      this.printerFiles = false
      this.$bvModal.show(this.modalId)
    },
    openPrinterFiles() {
      this.printerFiles = true
      this.$bvModal.show(this.modalId)
    },
    scrollToTop() {
      document.querySelector('#' + this.modalId).scrollTo(0, 0)
    },
    resetGcodesModal() {
      this.selectedGcodeId = null
    },
    onConnectClicked() {
      setTransientState(this.printer.id, 'Connecting')
      this.checkTransientState()

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
    onPauseToggled(ev) {
      if (this.printer.isPaused()) {
        if (this.printer.alertUnacknowledged()) {
          this.$emit('notAFailureClicked', ev, true)
        } else {
          setTransientState(this.printer.id, 'Resuming')
          this.checkTransientState()
          this.$emit('sendPrinterAction', this.printer.id, RESUME_PRINT, true)
        }
      } else {
        this.$swal.Confirm.fire({
          html: 'If you haven\'t changed the default configuration, the heaters will be turned off, and the print head will be z-lifted. The reversed will be performed before the print is resumed. <a target="_blank" href="https://www.obico.io/docs/user-guides/detection-print-job-settings#when-print-is-paused">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a>',
        }).then((result) => {
          if (result.value) {
            setTransientState(this.printer.id, 'Pausing')
            this.checkTransientState()
            this.$emit('sendPrinterAction', this.printer.id, PAUSE_PRINT, true)
          }
        })
      }
    },
    onCancelClicked() {
      this.$swal.Confirm.fire({
        text: 'Once cancelled, the print can no longer be resumed.',
      }).then((result) => {
        if (result.value) {
          setTransientState(this.printer.id, 'Cancelling')
          this.checkTransientState()
          this.$emit('sendPrinterAction', this.printer.id, CANCEL_PRINT, true)
        }
      })
    },
    checkTransientState() {
      const savedValue = getTransientState(this.printer.id, this.printer.status?.state?.text)

      if (!savedValue) {
        this.isPrinterInTransientState = false
        this.transientStateName = null
      } else if (savedValue === 'timeout') {
        this.isPrinterInTransientState = false
        this.transientStateName = null
        this.$swal.fire({
          icon: 'error',
          title: 'Printer State Timeout',
          text: 'Why it may happen: [link]', // TODO:
        })
      } else {
        this.isPrinterInTransientState = true
        this.transientStateName = savedValue.transientStateName
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  align-items: center
  justify-content: center
  padding-bottom: 2rem
  gap: 1rem
  @media (max-width: 480px)
    height: auto

.error-container, .warning-container
  width: 100%
  background-color: var(--color-danger)
  color: var(--color-on-danger)
  padding: 1rem
  border-radius: var(--border-radius-sm)
  text-align: center
  font-weight: normal
  margin-bottom: 1rem
  .title
    font-size: 1rem
    font-weight: bold
    margin-bottom: .5rem
  p
    font-size: 1rem
    font-weight: normal
  &.warning-container
    background-color: var(--color-warning)
    color: var(--color-on-warning)

p
  margin: 0
  font-size: 1.125rem
  text-align: center

.buttons
  display: flex
  align-items: center
  justify-content: center
  gap: 1rem
  margin-top: .5rem
  @media (max-width: 480px)
    flex-direction: column
    gap: 1rem

.big-icon
  font-size: 2rem
  &.warning
    color: var(--color-warning)
  &.danger
    color: var(--color-danger)

.custom-svg-icon
  height: 1.125rem
  width: 1.125rem
</style>
