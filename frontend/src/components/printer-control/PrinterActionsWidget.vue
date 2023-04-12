<template>
  <widget-template>
    <template #title>General</template>
    <template #content>
      <div class="wrapper">
        <template v-if="!printer.isOffline() && printer.hasError()">
          <i class="fa-solid fa-xmark big-icon danger"></i>
          <p>{{ printer.status.state.error }}</p>
        </template>

        <template v-if="printer.inUserInteractionRequired()">
          <i class="fa-solid fa-triangle-exclamation big-icon warning"></i>
          <p>Filament Change or User Interaction Required</p>
        </template>

        <template v-if="printer.inTransientState()">
          <b-spinner label="Processing..."></b-spinner>
          <p>{{ printer.status.state.text }}...</p>
        </template>

        <template v-else>
          <template v-if="!printer.isOffline() && !printer.isDisconnected() && printer.isActive()">
            <p>
              <span v-if="!printer.isPaused()">Printer is Curently Printing...</span>
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
              <b-button
                variant="danger"
                class="custom-button"
                @click="$emit('PrinterActionCancelClicked', $event)"
              >
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
              <div class="divider"></div>
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
              :disabled="connecting"
              @click="onConnectClicked"
            >
              <b-spinner v-if="connecting" small></b-spinner>
              <i v-else class="fa-brands fa-usb"></i>
              {{ connecting ? 'Contacting OctoPrint' : 'Connect' }}
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

        <b-modal v-if="printer" id="b-modal-gcodes" size="lg" @hidden="resetGcodesModal">
          <g-code-file-page
            v-if="selectedGcodeId"
            :is-popup="true"
            :target-printer-id="printer.id"
            :route-params="{
              fileId: selectedGcodeId,
              printerId: printerFiles ? printer.id : null,
            }"
            :on-close="() => $bvModal.hide('b-modal-gcodes')"
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
            :on-close="() => $bvModal.hide('b-modal-gcodes')"
            :saved-path="savedPath"
            scroll-container-id="b-modal-gcodes"
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

export default {
  name: 'PrinterActionsWidget',

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
  },

  data() {
    return {
      connectBtnClicked: false,
      selectedGcodeId: null,
      savedPath: [null],
      printerFiles: false,
    }
  },

  computed: {
    connecting() {
      return this.connectBtnClicked && this.printer.isDisconnected()
    },
  },

  methods: {
    openObicoFiles() {
      this.printerFiles = false
      this.$bvModal.show('b-modal-gcodes')
    },
    openPrinterFiles() {
      this.printerFiles = true
      this.$bvModal.show('b-modal-gcodes')
    },
    scrollToTop() {
      document.querySelector('#b-modal-gcodes').scrollTo(0, 0)
    },
    resetGcodesModal() {
      this.selectedGcodeId = null
    },
    onPauseToggled(ev) {
      if (this.printer.isPaused()) {
        this.$emit('PrinterActionResumeClicked', ev)
      } else {
        this.$emit('PrinterActionPauseClicked', ev)
      }
    },
    onConnectClicked(ev) {
      this.$emit('PrinterActionConnectClicked', ev)
      this.connectBtnClicked = true
      setTimeout(() => {
        this.connectBtnClicked = false
      }, 10 * 1000)
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
  height: 150px
  padding-bottom: 2rem
  gap: 1rem
  @media (max-width: 480px)
    height: auto

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

.divider
  flex: 0 0 1px
  height: 2rem
  background-color: var(--color-divider)
  margin: 0 .375rem
  transform: rotate(15deg)
  @media (max-width: 480px)
    display: none

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
