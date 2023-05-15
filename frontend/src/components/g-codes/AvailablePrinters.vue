<template>
  <div>
    <div v-if="printersLoading || !gcode" class="my-5 text-center">
      <b-spinner />
    </div>
    <div v-else>
      <div
        v-for="printer in printers"
        :key="`printer_${printer.id}`"
        class="printer-item"
        :class="{ active: selectedPrinter && printer.id === selectedPrinter.id }"
        @click="selectPrinter(printer)"
      >
        <div class="selected-indicator"></div>
        <div class="printer-name truncated" :title="printer.name">{{ printer.name }}</div>
        <div
          class="printer-status"
          :class="[
            printer.isPrintable() && !printer.isPrinterInTransientState
              ? 'text-success'
              : 'text-warning',
          ]"
        >
          {{
            printer.isPrinterInTransientState
              ? printer.transientStateName
              : printer.printabilityText()
          }}
        </div>
      </div>

      <p v-if="!printersLoading && !printers.length" class="text-center text-secondary mt-3 mb-3">
        No available printers
      </p>

      <button
        class="btn btn-primary mt-3"
        :disabled="!selectedPrinter || isSending || !selectedPrinter.isPrintable()"
        @click="onPrintClicked"
      >
        <b-spinner v-if="isSending" small />
        <div v-else>
          <div v-if="selectedPrinter" class="truncated">Print on {{ selectedPrinter.name }}</div>
          <div v-else class="truncated">Print</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedPrinter } from '@src/lib/normalizers'
import { sendToPrint, showRedirectModal } from './sendToPrint'
import { setTransientState, getTransientState } from '@src/lib/printer-transient-state'
import PrinterComm from '@src/lib/printer-comm'

export default {
  name: 'AvailablePrinters',

  components: {},

  props: {
    isPopup: {
      type: Boolean,
      default: false,
    },
    targetPrinterId: {
      type: Number,
      required: false,
      default: null,
    },
    gcode: {
      type: Object,
      default: null,
    },
    isCloud: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      printers: [],
      selectedPrinterId: null,
      printersLoading: true,
      isSending: false,
      printerStateCheckInterval: null,
      printerComms: {},
    }
  },

  computed: {
    selectedPrinter() {
      return this.printers.find((p) => p.id === this.selectedPrinterId)
    },
  },

  created() {
    this.fetchPrinters()
  },

  unmounted() {
    clearInterval(this.printerStateCheckInterval)
  },

  methods: {
    async fetchPrinters() {
      this.printersLoading = true

      let printers
      try {
        printers = await axios.get(urls.printers())
      } catch (e) {
        this.printersLoading = false
        console.error(e)
      }

      if (!printers?.data) {
        this.printersLoading = false
        return
      }

      printers = printers?.data
      printers = printers.map((p) => normalizedPrinter(p))

      if (this.targetPrinterId) {
        const selectedPrinter = printers.find((p) => p.id === this.targetPrinterId)
        this.printers = [selectedPrinter]
        if (selectedPrinter.isPrintable()) {
          this.selectedPrinterId = selectedPrinter.id
        }
      } else {
        this.printers = printers
        this.selectedPrinterId = printers.find((p) => p.isPrintable()).id
      }

      this.checkTransientStates()
      this.printerStateCheckInterval = setInterval(this.checkTransientStates, 1000)

      for (const printer of this.printers) {
        this.printerComms[printer.id] = PrinterComm(
          printer.id,
          urls.printerWebSocket(printer.id),
          (data) => {
            const index = this.printers.findIndex((p) => p.id === printer.id)
            this.$set(this.printers, index, normalizedPrinter(data, this.printers[index]))
          }
        )
        this.printerComms[printer.id].connect()
      }

      this.printersLoading = false
    },
    selectPrinter(printer) {
      if (!printer.isPrintable()) {
        this.$swal.Reject.fire({
          title: `${printer.name} isn't ready for print for one of the following reasons:`,
          html: `<ul style="text-align: left">
            <li>${printer.agentDisplayName()} is powered off or not connected to the Internet</li>
            <li>Printer is not connected to ${printer.agentDisplayName()}</li>
            <li>Printer is currently busy</li>
          </ul>`,
        })
        return
      }

      this.selectedPrinterId = printer.id
    },
    onPrintClicked() {
      if (!this.selectedPrinter?.id) return
      this.isSending = true

      setTransientState(this.selectedPrinter.id, 'Starting')
      sendToPrint({
        printerId: this.selectedPrinter.id,
        gcode: this.gcode,
        isCloud: this.isCloud,
        isAgentMoonraker: this.selectedPrinter.isAgentMoonraker(),
        Swal: this.$swal,
        onCommandSent: () => {
          if (this.isPopup) {
            this.$bvModal.hide('b-modal-gcodes' + this.selectedPrinter.id)
          }
        },
        onPrinterStatusChanged: () => {
          if (!this.isPopup) {
            showRedirectModal(this.$swal, () => this.$emit('refresh'), this.selectedPrinter.id)
          }

          this.isSending = false
          this.fetchPrinters()
        },
      })
    },
    checkTransientStates() {
      let oneIsStarting = false
      for (const printer of this.printers) {
        const index = this.printers.findIndex((p) => p.id === printer.id)
        const savedValue = getTransientState(printer.id, printer.status?.state?.text)

        if (!savedValue) {
          this.printers[index].isPrinterInTransientState = false
          this.printers[index].transientStateName = null
        } else if (savedValue === 'timeout') {
          this.printers[index].isPrinterInTransientState = false
          this.printers[index].transientStateName = null
          this.$swal.fire({
            icon: 'error',
            title: 'Printer State Timeout',
            text: 'Why it may happen: [link]', // TODO:
          })
        } else {
          this.printers[index].isPrinterInTransientState = true
          this.printers[index].transientStateName = savedValue.transientStateName

          if (savedValue.transientStateName === 'Starting') {
            oneIsStarting = true
            this.selectedPrinterId = printer.id
          }
        }
      }

      this.isSending = oneIsStarting ? true : false
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-item
  display: flex
  align-items: center
  border-radius: var(--border-radius-sm)
  border: 1px solid var(--color-divider)
  margin-bottom: 0.5rem
  padding: 0.75rem
  &:hover
    background-color: var(--color-hover)
    cursor: pointer

.selected-indicator
  --size: 0.875rem
  width: var(--size)
  height: var(--size)
  border-radius: var(--size)
  border: 1px solid var(--color-text-secondary)
  margin-right: 0.5rem

.printer-item.active
  background-color: var(--color-hover)
  .selected-indicator
    border-color: var(--color-text-primary)
    border-width: 3px

.printer-name
  flex: 1

.printer-status
  font-size: 0.875rem
  margin-left: 0.5rem

.btn
  width: 100%
</style>
