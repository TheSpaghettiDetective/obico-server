<template>
  <layout :isPopup="isPopup">

    <!-- Tob bar -->
    <template v-slot:topBarLeft>
      <a v-if="isPopup" @click.prevent="goBack" href="#" class="btn shadow-none icon-btn d-inline" title="Go Back">
        <i class="fas fa-chevron-left"></i>
      </a>
    </template>
    <template v-slot:topBarRight>
      <div>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item @click="renameFile">
            <i class="fas fa-edit"></i>Rename
          </b-dropdown-item>
          <b-dropdown-item @click="deleteFile">
            <span class="text-danger">
              <i class="fas fa-trash-alt"></i>Delete
            </span>
          </b-dropdown-item>
        </b-dropdown>
        <a v-if="onClose" @click.prevent="onClose" href="#" class="btn shadow-none icon-btn d-inline" title="Close">
          <i class="fas fa-times text-danger"></i>
        </a>
      </div>
    </template>

    <!-- Page content -->
    <template v-slot:content>
      <b-container v-if="loading || gcodeNotFound">
        <b-row>
          <b-col class="text-center mt-5">
            <div v-if="gcodeNotFound">
              <p>This G-Code file doesn't exists</p>
            </div>
            <div v-else>
              <b-spinner />
            </div>
          </b-col>
        </b-row>
      </b-container>
      <b-container v-else>
        <b-row>
          <b-col :lg="isPopup ? 12 : 8">
            <div class="card-container">
              <b-container fluid>
                <b-row>
                  <b-col>
                    <h1 class="file-name truncate-overflow-text">{{ gcode.filename }}</h1>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col sm="6">
                    <div class="file-info-line">
                      <div><i class="fas fa-history"></i>Uploaded</div>
                      <div class="value">{{ gcode.created_at.fromNow() }}</div>
                    </div>
                    <div class="file-info-line">
                      <div><i class="far fa-file-code"></i>File size</div>
                      <div class="value">{{ gcode.filesize }}</div>
                    </div>
                  </b-col>
                  <b-col sm="6">
                    <div class="file-info-line">
                      <div><i class="fas fa-circle"></i>Times printed</div>
                      <div class="value">{{ gcode.totalPrints }}</div>
                    </div>
                    <div class="file-info-line">
                      <div><i class="fas fa-circle text-success"></i>Succeeded</div>
                      <div class="value">{{ gcode.successPrints }}/{{ gcode.totalPrints }}</div>
                    </div>
                    <div class="file-info-line">
                      <div><i class="fas fa-circle text-danger"></i>Failed or cancelled</div>
                      <div class="value">{{ gcode.failedPrints }}/{{ gcode.totalPrints }}</div>
                    </div>
                  </b-col>
                </b-row>
              </b-container>
            </div>
          </b-col>

          <b-col :lg="isPopup ? 12 : 4" v-if="!printersLoading">
            <div class="card-container mt-4" :class="{'mt-lg-0': !isPopup}">
              <div
                class="printer-item"
                :class="{active: printer.id === selectedPrinter.id}"
                v-for="printer in availablePrinters"
                :key="`printer_${printer.id}`"
                @click="() => selectedPrinter = printer"
              >
                <div class="selected-indicator"></div>
                <div class="printer-name">{{ printer.name }}</div>
                <div class="printer-status text-success">Operational</div>
              </div>

              <p class="text-center text-secondary mt-3 mb-3" v-if="!printersLoading && !availablePrinters.length">No available printers</p>
              <p class="text-center text-secondary mt-3 mb-3" v-else-if="unavailablePrintersNum && !isPopup">{{unavailablePrintersNum}} printer(s) unavailable</p>

              <button class="btn btn-primary mt-3" :disabled="!selectedPrinter || isSending" @click="onPrintClicked">
                <b-spinner small v-if="isSending" />
                <div v-else>
                  <div class="truncate-overflow-text" v-if="selectedPrinter">Print on {{ selectedPrinter.name }}</div>
                  <div class="truncate-overflow-text" v-else>Print</div>
                </div>
              </button>
            </div>
          </b-col>

          <b-col :lg="isPopup ? 12 : 8">
            <div class="mt-5">
              <h2 class="section-title">{{ gcode.print_set.length ? 'Print history' : 'This file doesn\'t have any prints yet' }}</h2>
              <div class="print-history-card" v-for="print in gcode.print_set" :key="`print_${print.id}`">
                <div class="print-info">

                  <div class="result text-success font-weight-bold" v-if="print.finished_at">Succeeded</div>
                  <div class="result text-danger font-weight-bold" v-else-if="print.cancelled_at">Cancelled / Failed</div>
                  <div class="result font-weight-bold" v-else>Printing...</div>

                  <div class="printer truncate-overflow-text">Printer: {{ print.printer.name }}</div>
                  <div class="file truncate-overflow-text">File: {{ print.filename }}</div>

                  <div class="date">
                    Ended:
                    <span v-if="print.ended_at">{{ print.ended_at.fromNow() }}</span>
                    <span v-else>-</span>
                  </div>
                </div>
                <div class="poster" v-if="print.poster_url">
                  <div class="img" :style="{backgroundImage: `url(${print.poster_url})`}"></div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
      <rename-modal
        :item="gcode"
        @renamed="onItemRenamed"
        ref="renameModal"
      />
      <delete-confirmation-modal
        :item="gcode"
        @deleted="onItemDeleted"
        ref="deleteConfirmationModal"
      />
    </template>
  </layout>
</template>

<script>
import Layout from '@src/components/Layout.vue'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedGcode, normalizedPrinter } from '@src/lib/normalizers'
import PrinterComm from '@src/lib/printer_comm'
import get from 'lodash/get'
import RenameModal from './RenameModal.vue'
import DeleteConfirmationModal from './DeleteConfirmationModal.vue'
import { sendToPrint } from './sendToPrint'

const REDIRECT_TIMER = 3000

export default {
  name: 'GCodeDetailsPage',

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
    fileId: {
      type: Number,
      default: null,
    },
    targetPrinter: {
      type: Object,
      required: false,
    },
    onClose: {
      type: Function,
      required: false,
    },
  },

  data() {
    return {
      printers: [],
      selectedPrinter: null,
      gcode: null,
      loading: true,
      printersLoading: true,
      gcodeNotFound: false,
      isSending: false,
    }
  },

  created() {
    this.fetchGcode()
    this.fetchPrinters()
  },

  computed: {
    availablePrinters() {
      if (this.targetPrinter) {
        return this.selectedPrinter ? [this.selectedPrinter] : []
      }
      return this.printers.filter(p => p.status?.state?.text === 'Operational')
    },
    unavailablePrintersNum() {
      return this.printers.filter(p => p.status?.state?.text !== 'Operational').length
    },
  },

  methods: {
    goBack() {
      this.$emit('goBack')
    },
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
      this.printers = printers.map(p => normalizedPrinter(p))
      if (this.targetPrinter) {
        this.selectedPrinter = this.printers.find(p => p.id === this.targetPrinter.id)
      } else {
        this.selectedPrinter = this.availablePrinters[0]
      }

      this.printersLoading = false
    },
    async fetchGcode() {
      this.loading = true
      let file

      let fileId = this.fileId
      if (!this.isPopup) {
        fileId = this.$route.params.gcodeId
      }

      try {
        file = await axios.get(urls.gcodeFile(fileId))
      } catch (e) {
        this.loading = false
        console.error(e)
      }

      if (!file?.data) {
        this.loading = false
        this.gcodeNotFound = true
        return
      }

      file = file?.data
      this.gcode = normalizedGcode(file)

      this.gcode.print_set.sort((a, b) => {
        if (a.started_at > b.started_at) {
          return -1
        }
        if (a.started_at < b.started_at) {
          return 1
        }
        return 0
      })

      this.loading = false
    },
    onPrintClicked() {
      if (!this.selectedPrinter.id) return
      this.isSending = true

      sendToPrint(this.selectedPrinter.id, this.selectedPrinter.name, this.gcode, this.$swal, {
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
          this.fetchGcode()
        }
      })
    },
    renameFile() {
      this.$refs.renameModal.show()
    },
    onItemRenamed(newName) {
      this.gcode.filename = newName
    },
    deleteFile() {
      this.$refs.deleteConfirmationModal.show()
    },
    onItemDeleted() {
      if (!this.isPopup) {
        window.location.replace('/g_code_folders/')
      } else {
        this.$emit('goBack')
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.file-name
  font-size: 1.25rem
  margin-bottom: 1rem
  border-bottom: 1px solid var(--color-divider)
  padding-bottom: 1rem

.file-info-line
  display: flex
  justify-content: space-between
  margin-bottom: 0.5rem

  i
    margin-right: 0.375rem

  .value
    font-weight: 700

.section-title
  font-size: 1.25rem
  margin-bottom: 0.5rem

.print-history-card
  display: flex
  justify-content: space-between
  align-items: stretch
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-lg)
  margin-bottom: 1rem

.print-info
  flex: 1
  padding: 1rem
  overflow: hidden

  & > div
    margin-bottom: 0.25rem

.truncate-overflow-text
  width: 100%
  text-overflow: ellipsis
  overflow: hidden
  white-space: nowrap

.date
  color: var(--color-text-secondary)

.poster
  padding: .875rem
  .img
    border-radius: var(--border-radius-sm)
    background-size: cover
    background-position: center
    height: 100%
    width: 150px
    background-color: var(--color-hover)
    display: flex
    justify-content: center
    align-items: center
    color: var(--color-text-secondary)
    font-size: 0.875rem

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
