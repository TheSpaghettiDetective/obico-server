<template>
  <layout>

    <!-- Tob bar -->
    <template v-slot:topBarRight>
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
          <b-col lg=8>
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

          <b-col lg="4" v-if="!printersLoading">
            <div class="card-container mt-4 mt-lg-0">
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
              <p class="text-center text-secondary mt-3 mb-3" v-else-if="unavailablePrintersNum">{{unavailablePrintersNum}} printer(s) unavailable</p>

              <button class="btn btn-primary mt-3" :disabled="!selectedPrinter || isSending" @click="onPrintClicked">
                <b-spinner small v-if="isSending" />
                <div v-else>
                  <div class="truncate-overflow-text" v-if="selectedPrinter">Print on {{ selectedPrinter.name }}</div>
                  <div class="truncate-overflow-text" v-else>Print</div>
                </div>
              </button>
            </div>
          </b-col>

          <b-col lg="8">
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
                <div class="poster" v-if="gcode.poster_url">
                  <div class="img" :style="{backgroundImage: `url(${gcode.poster_url})`}">No image</div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
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

const REDIRECT_TIMER = 3000

export default {
  name: 'GCodeDetailsPage',

  components: {
    Layout,
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
      return this.printers.filter(p => p.status?.state?.text === 'Operational')
    },
    unavailablePrintersNum() {
      return this.printers.filter(p => p.status?.state?.text !== 'Operational').length
    },
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
      this.printers = printers.map(p => normalizedPrinter(p))
      // this.printers.push({...normalizedPrinter(printers[0]), id: 123, name: 'another one'})
      this.selectedPrinter = this.availablePrinters[0]

      this.printersLoading = false
    },
    async fetchGcode() {
      this.loading = true
      let file
      try {
        file = await axios.get(urls.gcodeFile(this.$route.params.gcodeId))
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

      const printerComm = PrinterComm(
        this.selectedPrinter.id,
        urls.printerWebSocket(this.selectedPrinter.id),
        (data) => {},
        (printerStatus) => {}
      )
      printerComm.connect(() => {
        printerComm.passThruToPrinter(
          {
            func: 'download',
            target: 'file_downloader',
            args: [this.gcode]
          },
          (err, ret) => {
            if (err || ret.error) {
              this.$swal.Toast.fire({
                icon: 'error',
                title: err ? err : ret.error,
              })
              return
            }

            this.showUploadingModal(ret)
          }
        )
      })
    },
    showUploadingModal(ret) {
      let targetPath = ret.target_path
      const printer = this.selectedPrinter

      this.$swal.Prompt.fire({
        html: `
          <div class="text-center">
            <i class="fas fa-spinner fa-spin fa-lg py-3"></i>
            <h5 class="py-3">
              Uploading G-Code to ${printer.name} ...
            </h5>
            <p>
              ${targetPath}
            </p>
          </div>
        `,
        showConfirmButton: false,
      })

      let checkPrinterStatus = async () => {
        await this.fetchPrinters()
        const targetPrinter = this.printers.find(p => p.id === printer.id)

        if (get(targetPrinter, 'status.state.text') === 'Operational') {
          setTimeout(checkPrinterStatus, 1000)
        } else {
          this.$swal.close()
          this.isSending = false

          this.showRedirectModal()
        }
      }

      checkPrinterStatus()
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
      this.$swal.Prompt.fire({
        title: 'New name',
        input: 'text',
        inputValue: this.gcode.filename,
        inputPlaceholder: 'New name',
        showCancelButton: true,
        confirmButtonText: 'Save',
        preConfirm: async (newName) => {
          if (!newName) {
            this.$swal.showValidationMessage('Name is required')
            return false
          }
          try {
            const url = urls.gcodeFile(this.gcode.id)
            await axios.patch(url, `filename=${newName}`)
          } catch (e) {
            this.$swal.showValidationMessage('Server error')
            console.log(e)
            return false
          }
          this.fetchGcode()
          return true
        },
      })
    },
    deleteFile() {
      this.$swal.Confirm.fire().then(async userAction => {
        if (userAction.isConfirmed) {
          try {
            const url = urls.gcodeFile(this.gcode.id)
            await axios.delete(url)
            window.location.replace('/g_code_folders/')
          } catch (e) {
            this.$swal.Reject.fire({
              title: 'Error',
              text: e.message,
            })
            console.log(e);
          }
        }
      })
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
