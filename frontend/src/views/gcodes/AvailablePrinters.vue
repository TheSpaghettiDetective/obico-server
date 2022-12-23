<template>
  <div>
    <div v-if="printersLoading || !gcode" class="my-5 text-center">
      <b-spinner />
    </div>
    <div v-else>
      <div
        class="printer-item"
        v-for="printer in printers"
        :key="`printer_${printer.id}`"
        :class="{active: selectedPrinter && printer.id === selectedPrinter.id}"
        @click="selectPrinter(printer)"
      >
        <div class="selected-indicator"></div>
        <div class="printer-name">{{ printer.name }}</div>
        <div
          class="printer-status"
          :class="{
            'text-success': printer.printAvailability.key === 'ready',
            'text-warning': printer.printAvailability.key === 'unavailable'
          }"
        >{{ printer.printAvailability.text }}</div>
      </div>

      <p class="text-center text-secondary mt-3 mb-3" v-if="!printersLoading && !printers.length">No available printers</p>

      <button class="btn btn-primary mt-3" :disabled="!selectedPrinter || isSending" @click="onPrintClicked">
        <b-spinner small v-if="isSending" />
        <div v-else>
          <div class="truncate-overflow-text" v-if="selectedPrinter">Print on {{ selectedPrinter.name }}</div>
          <div class="truncate-overflow-text" v-else>Print</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
import Layout from '@src/components/Layout.vue'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedPrinter } from '@src/lib/normalizers'
import RenameModal from './RenameModal.vue'
import DeleteConfirmationModal from './DeleteConfirmationModal.vue'
import { sendToPrint, getPrinterPrintAvailability } from './sendToPrint'

const REDIRECT_TIMER = 3000

export default {
  name: 'AvailablePrinters',

  components: {
    Layout,
    RenameModal,
    DeleteConfirmationModal,
  },

  props: {
    isPopup: {
      type: Boolean,
      default: false,
    },
    targetPrinterId: {
      type: Number,
      required: false,
    },
    gcode: {
      type: Object,
      default: null,
    },
    isCloud: {
      type: Boolean,
      default: true,
    }
  },

  data() {
    return {
      printers: [],
      selectedPrinter: null,
      printersLoading: true,
      isSending: false,
    }
  },

  created() {
    this.fetchPrinters()
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
      printers = printers.map(p => normalizedPrinter(p))
      printers = printers.map(p => ({...p, printAvailability: getPrinterPrintAvailability(p)}))

      if (this.targetPrinterId) {
        const selectedPrinter = printers.find(p => p.id === this.targetPrinterId)
        this.printers = [selectedPrinter]
        if (selectedPrinter.printAvailability.key === 'ready') {
          this.selectedPrinter = selectedPrinter
        }
      } else {
        this.printers = printers
        this.selectedPrinter = printers.filter(p => p.printAvailability.key === 'ready')[0]
      }

      this.printersLoading = false
    },
    selectPrinter(printer) {
      if (printer.printAvailability.key !== 'ready') {
        this.$swal.Reject.fire({
          title: `${printer.name} isn't ready for print for one of the following reasons:`,
          html: `<ul style="text-align: left">
            <li>${printer.agentDisplayName()} is powered off or not connected to the Inernet</li>
            <li>Printer is not connected to ${printer.agentDisplayName()}</li>
            <li>Printer is currently busy</li>
          </ul>`
        })
        return
      }

      this.selectedPrinter = printer
    },
    onPrintClicked() {
      if (!this.selectedPrinter?.id) return
      this.isSending = true

      sendToPrint({
        printerId: this.selectedPrinter.id,
        gcode: this.gcode,
        isCloud: this.isCloud,
        Swal: this.$swal,
        onCommandSent: () => {
          if (this.isPopup) {
            this.$bvModal.hide('b-modal-gcodes')
          }
        },
        onPrinterStatusChanged: () => {
          if (!this.isPopup) {
            this.showRedirectModal()
          }

          this.isSending = false
          this.fetchPrinters()
        }
      })
    },
    showRedirectModal() {
      let timerInterval
      this.$swal.Prompt.fire({
        html: `
          <div class="text-center">
            <h5 class="py-3">
              You'll be redirected to printers page in <strong>${Math.round(REDIRECT_TIMER / 1000)}</strong> seconds
            </h5>
          </div>
        `,
        timer: REDIRECT_TIMER,
        showConfirmButton: true,
        showCancelButton: true,
        confirmButtonText: 'Go now',
        onOpen: () => {
          const content = this.$swal.getHtmlContainer()
          const $ = content.querySelector.bind(content)

          timerInterval = setInterval(() => {
            this.$swal.getHtmlContainer().querySelector('strong')
              .textContent = (this.$swal.getTimerLeft() / 1000)
                .toFixed(0)
          }, 1000)
        },
        onClose: () => {
          clearInterval(timerInterval)
          timerInterval = null
        }
      }).then(result => {
        if (result.isConfirmed || result.dismiss === 'timer') {
          window.location.assign('/printers/')
        } else {
          this.$emit('refresh')
        }
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.truncate-overflow-text
  width: 100%
  text-overflow: ellipsis
  overflow: hidden
  white-space: nowrap

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

.btn
  width: 100%
</style>
