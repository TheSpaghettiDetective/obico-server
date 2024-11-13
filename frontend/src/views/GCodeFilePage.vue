<template>
  <page-layout :is-popup="isPopup">
    <!-- Tob bar -->
    <template #topBarLeft>
      <a
        v-if="isPopup"
        href="#"
        class="btn shadow-none icon-btn d-inline"
        :title="$t('Go Back')"
        @click.prevent="goBack"
      >
        <i class="fas fa-chevron-left"></i>
      </a>
    </template>
    <template #topBarRight>
      <div class="action-panel">
        <a
          v-if="canDownloadGcode"
          @click.prevent="downloadGcode"
          class="btn shadow-none icon-btn action-btn"
          :title="$t('Download file')"
        >
          <i class="fas fa-download"></i>
        </a>
        <!-- Rename -->
        <a
          v-if="isCloud"
          href="#"
          class="btn shadow-none icon-btn action-btn"
          :title="$t('Rename file')"
          @click.prevent="renameFile"
        >
          <i class="fas fa-edit"></i>
        </a>
        <!-- Delete -->
        <a
          v-if="isCloud"
          href="#"
          class="text-danger btn shadow-none icon-btn action-btn"
          :title="$t('Delete file')"
          @click.prevent="deleteFile"
        >
          <i class="fas fa-trash-alt"></i>
        </a>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="dropdownMenuOptions"
            @menuOptionClicked="onMenuOptionClicked"
          />
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
              <p>{{ $t("This G-Code file doesn't exists") }}</p>
            </div>
            <div v-else>
              <b-spinner />
            </div>
          </b-col>
        </b-row>
      </b-container>
      <b-container v-else fluid>
        <b-row>
          <b-col :lg="isPopup ? 12 : 5">
            <b-alert :show="isDeleted" variant="warning warning-block">
              {{$t("This file is deleted and unavailable for print")}}
            </b-alert>

            <!-- File details -->
            <g-code-details :file="gcode" :show-print-stats="true" :compact-view="false" />
            <jusprin-feedback v-if="isCloud" class="card-container jusprin-feedback" :g-code-file-id="gcode.id" />
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
          </b-col>
          <b-col :lg="isPopup ? 12 : 7">
            <!-- Print history -->
            <div class="print-history" :class="{ 'full-width': isPopup || isDeleted }">
              <h2 class="section-title mb-3">{{ $t("Print History") }}</h2>
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
                  {{$t("This file doesn't have any prints yet")}}
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
import { printerCommManager } from '@src/lib/printer-comm'
import {
  listPrinterLocalGCodesMoonraker,
  listPrinterLocalGCodesOctoPrint,
} from '@src/lib/printer-local-comm'
import PrintHistoryItem from '@src/components/prints/PrintHistoryItem.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import GCodeDetails from '@src/components/GCodeDetails.vue'
import JusprinFeedback from '@src/components/g-codes/JusprinFeedback.vue'

export default {
  name: 'GCodeFilePage',

  components: {
    PageLayout,
    RenameModal,
    DeleteConfirmationModal,
    availablePrinters,
    PrintHistoryItem,
    CascadedDropdown,
    GCodeDetails,
    JusprinFeedback,
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
    dropdownMenuOptions() {
      const menuOptions = [
        {
          key: 'renameFile',
          icon: 'fas fa-edit',
          title: this.$i18next.t(`Rename file`),
          callback: true,
        },
        {
          key: 'deleteFile',
          icon: 'fas fa-trash-alt',
          customMenuOptionClass: 'text-danger',
          title: this.$i18next.t(`Delete file`),
          callback: true,
        },
      ]

      if (this.canDownloadGcode) {
        menuOptions.unshift({
          key: 'downloadGcode',
          icon: 'fas fa-download',
          title: this.$i18next.t(`Download file`),
          callback: true,
        })
      }

      return menuOptions
    },
    canDownloadGcode() {
      return this.gcode?.url && this.gcode?.safe_filename
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
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'renameFile') {
        this.renameFile()
      } else if (menuOptionKey === 'deleteFile') {
        this.deleteFile()
      } else if (menuOptionKey === 'downloadGcode') {
        this.downloadGcode()
      }
    },
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
          this.errorDialog(error, `${this.$i18next.t('Host printer for this gcode not found')}`)
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
            ...normalizedGcode(file),
            print_set: [],
          }
          if (file.path && file.hash && this.getRouteParam('printerId')) {
            const safeFilename = file.path.replace(/^.*[\\/]/, '')
            try {
              let response = await axios.get(urls.gcodeFiles(), {
                params: {
                  resident_printer: this.getRouteParam('printerId'),
                  safe_filename: safeFilename,
                  agent_signature: `md5:${file.hash}`,
                },
              })
              const gcodeFileOnServer = get(response, 'data.results[0]')
              if (gcodeFileOnServer) {
                const cloudCopy = normalizedGcode(gcodeFileOnServer)
                this.gcode.print_set = cloudCopy.print_set
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
        this.printerComm = printerCommManager.getOrCreatePrinterComm(
          this.selectedPrinterId,
          urls.printerWebSocket(this.selectedPrinterId)
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
    async downloadGcode() {
      const fileUrl = this.gcode.url

      const response = await fetch(fileUrl);
      const blob = await response.blob();

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = this.gcode.safe_filename

      document.body.appendChild(link);

      link.click();

      URL.revokeObjectURL(link.href);
      document.body.removeChild(link);
    }
  },
}
</script>

<style lang="sass" scoped>
.warning-block
  margin-bottom: var(--gap-between-blocks)

.available-printers,
.jusprin-feedback
  margin-top: var(--gap-between-blocks)
  &.full-width
    margin-top: 15px

.print-history
  &.full-width
    margin-top: 30px
  @media (max-width: 991px)
    margin-top: 30px

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
