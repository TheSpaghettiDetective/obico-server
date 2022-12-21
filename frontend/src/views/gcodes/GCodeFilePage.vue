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
        <b-dropdown v-if="isCloud" right no-caret toggle-class="icon-btn">
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
                  <b-col sm="6" v-show="isCloud">
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

            <available-printers
              class="card-container mt-4"
              :class="[isPopup ? 'd-lg-block' : 'd-lg-none']"
              :isPopup="isPopup"
              :targetPrinterId="targetPrinterId || selectedPrinterId"
              :gcode="gcode"
              :isCloud="isCloud"
              @refresh="onRefresh"
            />

            <div class="mt-5" v-if="isCloud">
              <h2 class="section-title">Print history</h2>
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
              <div v-if="!gcode.print_set.length">
                <div class="print-history-card p-4 justify-content-center text-secondary">
                  This file doesn't have any prints yet
                </div>
              </div>
            </div>
          </b-col>

          <b-col :lg="isPopup ? 12 : 4">
            <available-printers
              class="card-container d-none"
              :class="[isPopup ? 'd-lg-none' : 'd-lg-block']"
              :isPopup="isPopup"
              :targetPrinterId="targetPrinterId || Number(selectedPrinterId)"
              :gcode="gcode"
              :isCloud="isCloud"
              @refresh="onRefresh"
            />
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
import { normalizedGcode } from '@src/lib/normalizers'
import RenameModal from './RenameModal.vue'
import DeleteConfirmationModal from './DeleteConfirmationModal.vue'
import availablePrinters from './AvailablePrinters.vue'
import PrinterComm from '@src/lib/printer_comm'
import { listFiles } from './localFiles'


export default {
  name: 'GCodeDetailsPage',

  components: {
    Layout,
    RenameModal,
    DeleteConfirmationModal,
    availablePrinters,
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
    onClose: {
      type: Function,
      required: false,
    },
    routeParams: {
      type: Object,
      default: () => {
        return {
          fileId: null,
          printerId: null,
        }
      }
    }
  },

  data() {
    return {
      gcode: null,
      loading: true,
      gcodeNotFound: false,
    }
  },

  created() {
    this.selectedPrinterId = Number(this.getRouteParam('printerId')) || null
    this.gcodeId = this.getRouteParam('fileId')
    this.fetchGcode()
  },

  computed: {
    isCloud() {
      return !Boolean(this.selectedPrinterId)
    },
  },

  methods: {
    getRouteParam(name) {
      return this.isPopup ? this.routeParams[name] : this.$route.params[name]
    },
    goBack() {
      this.$emit('goBack')
    },
    async fetchLocalFile() {
      if (!this.printerComm) {
        return
      }
      this.loading = true

      const decodedPath = decodeURIComponent(this.gcodeId)
      const filename = decodedPath.split('/').at(-1)
      const path = filename === decodedPath ? '' : decodedPath.slice(0, decodedPath.length - filename.length - 1)

      listFiles(this.printerComm, {
        query: filename,
        path,
        onRequestEnd: (result) => {
          this.loading = false
          if (result?.files?.length) {
            const file = result.files.filter(f => f.path === decodedPath)[0]
            if (!file) {
              this.gcodeNotFound = true
              return
            }
            this.gcode = {
              ...file,
              print_set: [],
            }
          } else {
            this.gcodeNotFound = true
          }
        },
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
</style>
