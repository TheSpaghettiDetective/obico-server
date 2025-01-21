<template>
  <div>
    <div v-if="printersLoading || !gcode" class="my-5 text-center">
      <b-spinner />
    </div>
    <div v-else class="text-center">
      <div v-if="!targetPrinterId" class="mb-3">
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
            :class="[printer.isPrintable() ? 'text-success' : 'text-warning']"
          >
            {{ printer.printabilityText() }}
          </div>
        </div>

        <p v-if="!printersLoading && !printers.length" class="text-center text-secondary mt-3 mb-3">
          {{$t("No available printers")}}
        </p>
      </div>

      <button
        class="btn btn-primary d-inline-flex align-items-center justify-content-center"
        :disabled="!selectedPrinter || isSending || !selectedPrinter.isPrintable()"
        @click="onPrintClicked"
      >
        <b-spinner v-if="isSending" small class="mr-1" />
        <div v-if="selectedPrinter" class="truncated">{{$t('Print on')}} {{ selectedPrinter.name }}</div>
        <div v-else class="truncated">{{ $t("Print") }}</div>
      </button>
    </div>
  </div>
</template>

<script>
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedPrinter } from '@src/lib/normalizers'
import { sendToPrint, showRedirectModal, confirmPrint } from './sendToPrint'
import { printerCommManager } from '@src/lib/printer-comm'

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
      selectedPrinter: null,
      printersLoading: true,
      printerStateCheckInterval: null,
      printerComms: {},
    }
  },

  computed: {
    isSending() {
      return this.printers.some(
        (p) => p.calculatedState() === 'Starting' || p.calculatedState() === 'G-Code Downloading'
      )
    },
  },

  created() {
    this.fetchPrinters()
  },

  methods: {
    async fetchPrinters() {
      this.printersLoading = true

      const resp = await axios.get(urls.printers())
      if (!resp?.data) {
        this.printersLoading = false
        return
      }

      const printers = resp?.data.map((p) => normalizedPrinter(p))
      if (this.targetPrinterId) {
        const selectedPrinter = printers.find((p) => p.id === this.targetPrinterId)
        this.printers = [selectedPrinter]
        if (selectedPrinter.isPrintable()) {
          this.selectedPrinter = selectedPrinter
        }
      } else {
        this.printers = printers
        this.selectedPrinter = printers.find((p) => p.isPrintable()) || null
      }

      for (const printer of this.printers) {
        this.printerComms[printer.id] = printerCommManager.getOrCreatePrinterComm(
          printer.id,
          urls.printerWebSocket(printer.id),
          {
            onPrinterUpdateReceived: (data) => {
              const index = this.printers.findIndex((p) => p.id === printer.id)
              this.$set(this.printers, index, normalizedPrinter(data, this.printers[index]))
            },
          }
        )
        this.printerComms[printer.id].connect()
      }

      this.printersLoading = false
    },
    selectPrinter(printer) {
      if (!printer.isPrintable()) {
        this.$swal.Reject.fire({
          title: `${this.$i18next.t(`{name} isn't ready for print for one of the following reasons`,{name:printer.name})}:`,
          html: `<ul style="text-align: left">
            <li>${this.$i18next.t(`{name} is powered off or not connected to the Internet`,{name:printer.agentDisplayName()})}</li>
            <li>${this.$i18next.t("Printer is not connected to {name}",{name:printer.agentDisplayName()})}</li>
            <li>${this.$i18next.t("Printer is currently busy")}</li>
          </ul>`,
        })
        return
      }

      this.selectedPrinter = printer
    },
    onPrintClicked() {
      if (!this.selectedPrinter?.id) return

      confirmPrint(this.gcode, this.selectedPrinter).then(() => {
        sendToPrint({
          printer: this.selectedPrinter,
          gcode: this.gcode,
          isCloud: this.isCloud,
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

            this.fetchPrinters()
          },
        })
      })
      return
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-item
  display: flex
  align-items: center
  text-align: left
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
  max-width: 100%
</style>

