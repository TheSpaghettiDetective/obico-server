<template>
  <page-layout :is-popup="isPopup">
    <!-- Tob bar -->
    <template #topBarLeft>
      <a
        v-if="isPopup"
        href="#"
        class="btn shadow-none icon-btn d-inline"
        title="Go Back"
        @click.prevent="goBack"
      >
        <i class="fas fa-chevron-left"></i>
      </a>
    </template>
    <template #topBarRight>
      <div>
        <b-dropdown v-if="isCloud" right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item @click="renameFile"> <i class="fas fa-edit"></i>Rename </b-dropdown-item>
          <b-dropdown-item @click="deleteFile">
            <span class="text-danger"> <i class="fas fa-trash-alt"></i>Delete </span>
          </b-dropdown-item>
        </b-dropdown>
        <a
          v-if="onClose"
          href="#"
          class="btn shadow-none icon-btn d-inline"
          title="Close"
          @click.prevent="onClose"
        >
          <i class="fas fa-times text-danger"></i>
        </a>
      </div>
    </template>

    <!-- Page content -->
    <template #content>
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
      <b-container v-else fluid="xl">
        <b-row>
          <b-col :lg="isDeleted ? 8 : 12" :offset-lg="isDeleted ? 2 : 0">
            <b-alert :show="isDeleted" variant="warning warning-block">
              This file is deleted and unavailable for print
            </b-alert>

            <!-- File info -->
            <div class="card-container file-info" :class="{ 'full-width': isPopup || isDeleted }">
              <b-container fluid>
                <b-row>
                  <b-col>
                    <h1 class="file-name overflow-truncated">
                      {{ gcode.filename }}
                    </h1>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col :sm="isCloud ? 6 : 12">
                    <div class="file-info-line">
                      <div><i class="fas fa-history"></i>Uploaded</div>
                      <div class="value">{{ gcode.created_at.fromNow() }}</div>
                    </div>
                    <div class="file-info-line">
                      <div><i class="far fa-file-code"></i>File size</div>
                      <div class="value">{{ gcode.filesize }}</div>
                    </div>
                  </b-col>
                  <b-col v-show="isCloud" sm="6">
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
            <!-- Available printers -->
            <available-printers
              v-if="!isDeleted"
              class="card-container available-printers"
              :class="{ 'full-width': isPopup }"
              :is-popup="isPopup"
              :target-printer-id="targetPrinterId || selectedPrinterId"
              :gcode="gcode"
              :is-cloud="isCloud"
              @refresh="onRefresh"
            />
            <!-- Print history -->
            <div class="print-history" :class="{ 'full-width': isPopup || isDeleted }">
              <h2 class="section-title">Print history</h2>
              <div v-if="gcode.print_set.length">
                <print-history-item
                  v-for="print of gcode.print_set"
                  :key="`print_${print.id}`"
                  :print="print"
                  class="print-item"
                ></print-history-item>
              </div>
              <div v-else>
                <div class="card-container p-4 justify-content-center text-secondary">
                  This file doesn't have any prints yet
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
      <rename-modal ref="renameModal" :item="gcode" @renamed="onItemRenamed" />
      <delete-confirmation-modal
        ref="deleteConfirmationModal"
        :item="gcode"
        @deleted="onItemDeleted"
      />
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import filter from 'lodash/filter'
import get from 'lodash/get'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedGcode, normalizedPrinter } from '@src/lib/normalizers'
import RenameModal from '@src/components/g-codes/RenameModal.vue'
import DeleteConfirmationModal from '@src/components/g-codes/DeleteConfirmationModal.vue'
import availablePrinters from '@src/components/g-codes/AvailablePrinters.vue'
import PrinterComm from '@src/lib/printer-comm'
import {
  listPrinterLocalGCodesMoonraker,
  listPrinterLocalGCodesOctoPrint,
} from '@src/lib/printer-local-comm'
import PrintHistoryItem from '@src/components/prints/PrintHistoryItem.vue'

export default {
  name: 'GCodeFilePage',

  components: {
    PageLayout,
    RenameModal,
    DeleteConfirmationModal,
    availablePrinters,
    PrintHistoryItem,
  },

  props: {
    isPopup: {
      type: Boolean,
      default: false,
    },
    targetPrinterId: {
      type: Number,
      default: null,
    },
    onClose: {
      type: Function,
      default: null,
    },
    routeParams: {
      type: Object,
      default: () => {
        return {
          fileId: null,
          printerId: null,
        }
      },
    },
  },

  data() {
    return {
      gcode: null,
      printer: null,
      loading: true,
      gcodeNotFound: false,
    }
  },

  computed: {
    isCloud() {
      return !this.selectedPrinterId
    },
    isDeleted() {
      return !!this.gcode?.deleted
    },
  },

  async created() {
    this.selectedPrinterId = Number(this.getRouteParam('printerId')) || null
    if (this.selectedPrinterId) {
      await this.fetchPrinter()
    }
    this.gcodeId = this.getRouteParam('fileId')
    this.fetchGcode()
  },

  methods: {
    getRouteParam(name) {
      return this.isPopup ? this.routeParams[name] : this.$route.params[name]
    },
    goBack() {
      this.$emit('goBack')
    },
    async fetchPrinter() {
      return axios
        .get(urls.printer(this.selectedPrinterId))
        .then((response) => {
          this.printer = normalizedPrinter(response.data)
        })
        .catch((error) => {
          this._showErrorPopup(error, 'Host printer for this gcode not found')
        })
    },
    async fetchLocalFile() {
      if (!this.printerComm) {
        return
      }
      this.loading = true

      const decodedPath = decodeURIComponent(this.gcodeId)
      const filename = decodedPath.split('/').at(-1)
      const dir_path =
        filename === decodedPath
          ? ''
          : decodedPath.slice(0, decodedPath.length - filename.length - 1)

      const getPrinterLocalGCode = this.printer.isAgentMoonraker()
        ? listPrinterLocalGCodesMoonraker
        : listPrinterLocalGCodesOctoPrint

      getPrinterLocalGCode(this.printerComm, dir_path, null)
        .then((result) => {
          return { files: filter(get(result, 'files', []), (f) => f.filename == filename) }
        })
        .then(async (result) => {
          this.loading = false
          if (result?.files?.length === 0) {
            this.gcodeNotFound = true
            return
          }

          const file = result?.files[0]
          this.gcode = {
            ...file,
            print_set: [],
          }
          if (file.path && file.hash && this.getRouteParam('printerId')) {
            const safeFilename = file.path.replace(/^.*[\\/]/, '')
            try {
              let response = await axios.get(
                urls.gcodeFiles({
                  resident_printer: this.getRouteParam('printerId'),
                  safe_filename: safeFilename,
                  agent_signature: `md5:${file.hash}`,
                })
              )
              const gcodeFileOnServer = get(response, 'data.results[0]')
              if (gcodeFileOnServer) {
                this.gcode = { ...this.gcode, ...normalizedGcode(gcodeFileOnServer) }
              }
            } catch (e) {
              console.error(e)
            }
          }
        })
        .catch((err) => {
          this.gcodeNotFound = true
        })
    },
    async fetchGcode() {
      if (this.selectedPrinterId) {
        this.printerComm = PrinterComm(
          this.selectedPrinterId,
          urls.printerWebSocket(this.selectedPrinterId),
          (data) => {},
          (printerStatus) => {}
        )
        this.printerComm.connect(this.fetchLocalFile)
        return
      }

      this.loading = true
      const fileId = this.getRouteParam('fileId')
      let file

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
      this.loading = false
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
        window.location.replace('/g_code_folders/cloud/')
      } else {
        this.$emit('goBack')
      }
    },
    onRefresh() {
      this.$router.go()
    },
  },
}
</script>

<style lang="sass" scoped>
.warning-block
  margin-bottom: var(--gap-between-blocks)

.file-info, .print-history
  width: 60%
  display: inline-block
  &.print-history
    padding-top: 10px
    margin-top: 30px

.available-printers
  width: calc(40% - 30px)
  float: right

.file-info, .print-history, .available-printers
  &.full-width
    width: 100%
    &.print-history, &.available-printers
      margin-top: 15px
  @media (max-width: 996px)
    width: 100%
    &.print-history, &.available-printers
      margin-top: 15px

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

.print-item
  margin-bottom: 10px
</style>
