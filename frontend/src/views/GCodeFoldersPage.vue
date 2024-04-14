<template>
  <page-layout :is-popup="isPopup">
    <!-- Tob bar -->
    <template #topBarLeft>
      <a
        v-if="isPopup && parentFolder !== null"
        href="#"
        class="btn shadow-none icon-btn d-inline"
        title="Go Back"
        @click.prevent="goBack"
      >
        <i class="fas fa-chevron-left"></i>
      </a>
      <div v-if="!isPopup && isCloud" class="actions-with-selected-desktop">
        <b-form-group class="m-0">
          <b-form-checkbox
            :checked="allSelected"
            size="md"
            @click.native.capture.stop.prevent="toggleSelectAll"
          ></b-form-checkbox>
        </b-form-group>
        <div>
          <span v-show="!selectedItemsCount" class="label" @click="toggleSelectAll"
            >{{ $t("Select all") }}</span
          >
          <b-dropdown
            v-show="selectedItemsCount"
            toggle-class="btn btn-sm actions-with-selected-btn"
          >
            <template #button-content>
              {{ selectedItemsCount }} item{{ selectedItemsCount === 1 ? '' : 's' }}
              {{$t("selected")}}
            </template>
            <b-dropdown-item>
              <div @click="moveSelectedItems"><i class="fas fa-arrows-alt"></i>{{ $t("Move") }}</div>
            </b-dropdown-item>
            <b-dropdown-item>
              <div class="text-danger" @click="deleteSelectedItems">
                <i class="far fa-trash-alt"></i>{{$t("Delete")}}
              </div>
            </b-dropdown-item>
          </b-dropdown>
        </div>
      </div>

      <search-input class="search-input mr-3" @input="updateSearch"></search-input>
    </template>
    <template #topBarRight>
      <div class="action-panel">
        <!-- Create folder -->
        <a
          v-if="isCloud"
          href="#"
          class="btn shadow-none icon-btn d-none d-md-inline"
          title="Create folder"
          @click.prevent="createFolder"
        >
          <i class="fas fa-folder-plus"></i>
        </a>
        <!-- Select storage -->
        <b-dropdown right no-caret toggle-class="action-btn icon-btn">
          <template #button-content>
            <i class="fas fa-server"></i>
          </template>
          <b-dropdown-text class="small text-secondary">{{ $t("STORAGE") }}</b-dropdown-text>
          <b-dropdown-item @click="switchToCloudStorage">
            <div class="dropdown-text-group">
              <i
                class="fas fa-check text-primary"
                :style="{ visibility: isCloud ? 'visible' : 'hidden' }"
              ></i>
              <div class="text">
                <div class="title">{{ $syndicateText.brandName }} {{$t("Cloud")}}</div>
              </div>
            </div>
          </b-dropdown-item>
          <b-dropdown-item
            v-for="printer in printers"
            :key="printer.id"
            @click="() => switchToPrinterStorage(printer)"
          >
            <div class="dropdown-text-group">
              <i
                class="fas fa-check text-primary"
                :style="{ visibility: selectedPrinterId === printer.id ? 'visible' : 'hidden' }"
              ></i>
              <div class="text">
                <div class="title">{{ printer.name }}</div>
                <div
                  class="subtitle"
                  :class="[isPrinterBrowsable(printer) ? 'text-success' : 'text-warning']"
                >
                  {{ printerBrowsabilityText(printer) }}
                </div>
              </div>
            </div>
          </b-dropdown-item>
        </b-dropdown>
        <!-- Sorting -->
        <b-dropdown right no-caret toggle-class="action-btn icon-btn" title="Sort By">
          <template #button-content>
            <i class="fas fa-sort-amount-down"></i>
          </template>
          <sorting-dropdown
            :local-storage-prefix="sortingLocalStoragePrefix"
            :sorting-options="sortingOptions"
            :sorting-value="sortingValue"
            @onSortingUpdated="onSortingUpdated"
          />
        </b-dropdown>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>

          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="mobileMenuOptions"
            @menuOptionClicked="onMenuOptionClicked"
          >
            <template #sorting>
              <sorting-dropdown
                :local-storage-prefix="sortingLocalStoragePrefix"
                :sorting-options="sortingOptions"
                :sorting-value="sortingValue"
                @onSortingUpdated="onSortingUpdated"
              />
            </template>
            <template #storage>
              <b-dropdown-text class="small text-secondary">{{ $t("STORAGE") }}</b-dropdown-text>
              <b-dropdown-item
                @click="
                  () => {
                    switchToCloudStorage()
                    $refs.cascadedDropdown.resetMenuExpanded()
                  }
                "
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: isCloud ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="text">
                    <div class="title">{{ $syndicateText.brandName }} {{$t("Cloud")}}</div>
                  </div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item
                v-for="printer in printers"
                :key="printer.id"
                @click="
                  () => {
                    switchToPrinterStorage(printer)
                    $refs.cascadedDropdown.resetMenuExpanded()
                  }
                "
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: selectedPrinterId === printer.id ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="text">
                    <div class="title">{{ printer.name }}</div>
                    <div
                      class="subtitle"
                      :class="[isPrinterBrowsable(printer) ? 'text-success' : 'text-warning']"
                    >
                      {{ printerBrowsabilityText(printer) }}
                    </div>
                  </div>
                </div>
              </b-dropdown-item>
            </template>
          </cascaded-dropdown>
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
      <b-container>
        <b-row>
          <b-col>
            <vue-dropzone
              v-if="isCloud"
              id="dropzone"
              ref="gcodesDropzone"
              class="upload-box"
              :options="dropzoneOptions"
              :use-custom-slot="true"
              @vdropzone-queue-complete="gcodeUploadSuccess"
              @vdropzone-error="gcodeUploadError"
              @vdropzone-sending="addParentFolderParam"
            >
              <div class="dz-message needsclick">
                <i class="fas fa-upload fa-2x"></i> <br />
                <div>{{ $t("G-Code file (*.gcode, *.gco, or *.g) only.") }}</div>
                <div>{{ $t('Up to {maxFilesize} MB each file, {maxTotalFilesize} GB total.',{maxFilesize,maxTotalFilesize}) }}</div>
              </div>
            </vue-dropzone>

            <div v-if="!isCloud && isAgentMoonraker && searchStateIsActive" class="notice-block">
              <div class="icon">
                <i class="fas fa-info"></i>
              </div>
              <p class="message">{{ $t("Search in Klipper printers works only for current directory") }}</p>
            </div>

            <g-code-file-structure
              ref="gCodeFileStructure"
              :is-cloud="isCloud"
              :is-popup="isPopup"
              :search-state-is-active="searchStateIsActive"
              :search-in-progress="searchInProgress"
              :folders="folders"
              :files="files"
              :target-printer="targetPrinter"
              :nothing-found="nothingFound"
              :loading="loading"
              :scroll-container-id="scrollContainerId"
              :no-more-folders="noMoreFolders"
              :no-more-files="noMoreFiles"
              :local-files-loading="localFilesLoading"
              @openFolder="openFolder"
              @openFile="openFile"
              @renameItem="renameItem"
              @moveItem="moveItem"
              @deleteItem="deleteItem"
              @print="onPrintClicked"
              @fetchMore="fetchFilesAndFolders"
              @selectFiles="onSelectFiles"
              @selectFolders="onSelectFolders"
            />
          </b-col>
        </b-row>
      </b-container>
      <rename-modal
        ref="renameModal"
        :item="activeItem"
        :pre-confirm="verifyItemRename"
        @renamed="onItemRenamed"
      />
      <move-modal
        ref="moveModal"
        :item="activeItem"
        :items="activeItems"
        :item-parent-folder-id="parentFolder"
        :target-printer="targetPrinter"
        :scroll-container-id="scrollContainerId"
        :sorting-value="sortingValue"
        @moved="onItemMoved"
      />
      <delete-confirmation-modal
        ref="deleteConfirmationModal"
        :item="activeItem"
        @deleted="onItemDeleted"
      />
      <new-folder-modal
        ref="newFolderModal"
        :pre-confirm="verifyNewFolder"
        :parent-folder-id="parentFolder"
        @created="onFolderCreated"
      />
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import urls from '@config/server-urls'
import axios from 'axios'
import {
  normalizedGcode,
  normalizedGcodeFolder,
  normalizedPrinter,
  PrintStatus,
} from '@src/lib/normalizers'
import { user } from '@src/lib/page-context'
import SearchInput from '@src/components/SearchInput.vue'
import { getCsrfFromDocument } from '@src/lib/utils'
import NewFolderModal from '@src/components/g-codes/NewFolderModal.vue'
import RenameModal from '@src/components/g-codes/RenameModal.vue'
import MoveModal from '@src/components/g-codes/MoveModal.vue'
import DeleteConfirmationModal from '@src/components/g-codes/DeleteConfirmationModal.vue'
import { sendToPrint, confirmPrint } from '@src/components/g-codes/sendToPrint'
import { printerCommManager } from '@src/lib/printer-comm'
import {
  listPrinterLocalGCodesOctoPrint,
  listPrinterLocalGCodesMoonraker,
} from '@src/lib/printer-local-comm'
import GCodeFileStructure from '@src/components/g-codes/GCodeFileStructure.vue'
import SortingDropdown, { restoreSortingValue } from '@src/components/SortingDropdown'
import CascadedDropdown from '@src/components/CascadedDropdown'
import i18n from '@src/i18n/i18n.js'

// Waiting time (ms) before asking server for search results
const SEARCH_API_CALL_DELAY = 1000

const PAGE_SIZE = 24

const SortingLocalStoragePrefix = 'gcodesSorting'
const SortingOptions = {
  options: [
    { title: `${i18n.t('Name')}`, key: 'filename', folderKey: 'name' },
    { title: `${i18n.t('Size')}`, key: 'num_bytes' },
    { title: `${i18n.t('Created')}`, key: 'created_at', folderKey: 'created_at' },
  ],
  default: { sorting: 'created_at', direction: 'desc' },
}

export default {
  name: 'GCodeFoldersPage',

  components: {
    PageLayout,
    SearchInput,
    vueDropzone: vue2Dropzone,
    GCodeFileStructure,
    RenameModal,
    MoveModal,
    DeleteConfirmationModal,
    NewFolderModal,
    SortingDropdown,
    CascadedDropdown,
  },

  props: {
    isPopup: {
      type: Boolean,
      default: false,
    },
    onClose: {
      type: Function,
      default: null,
    },
    scrollContainerId: {
      type: String,
      default: null,
    },
    targetPrinter: {
      type: Object,
      default: null,
    },
    savedPath: {
      type: Array,
      default: () => [],
    },
    routeParams: {
      type: Object,
      default: () => {
        return {
          printerId: null,
          parentFolder: null,
        }
      },
    },
  },

  data() {
    return {
      PrintStatus,
      csrf: null,
      user: null,
      loading: false,
      parentFolder: null,
      path: [],
      files: [],
      folders: [],
      noMoreFolders: false,
      noMoreFiles: false,
      currentFoldersPage: 1,
      currentFilesPage: 1,

      // Sorting
      sortingLocalStoragePrefix: SortingLocalStoragePrefix,
      sortingOptions: SortingOptions,
      sortingValue: restoreSortingValue(SortingLocalStoragePrefix, SortingOptions),

      searchQuery: null,
      searchStateIsActive: false,
      searchTimeoutId: null,

      activeItem: null,
      activeItems: null,

      // local storage:
      printers: [],
      selectedPrinterId: undefined,
      selectedPrinterComm: undefined,
      localFilesLoading: false,

      selectedFolders: new Set(),
      selectedFiles: new Set(),
    }
  },

  computed: {
    selectedItemsCount() {
      return this.selectedFiles.size + this.selectedFolders.size
    },
    allSelected() {
      const itemsCount = this.files.length + this.folders.length
      return this.selectedItemsCount === itemsCount && itemsCount !== 0
    },
    mobileMenuOptions() {
      const options = [
        {
          key: 'storage',
          icon: 'fas fa-server',
          title: `${this.$i18next.t(`File storage`)}`,
          expandable: true,
        },
        {
          key: 'sorting',
          icon: 'fas fa-sort-amount-down',
          title: `${this.$i18next.t(`Sort`)}`,
          expandable: true,
        },
      ]

      if (this.isCloud) {
        options.unshift({
          key: 'createFolder',
          icon: 'fas fa-folder-plus',
          title: `${this.$i18next.t('Create folder')}`,
          callback: true,
        })
      }

      return options
    },
    isAgentMoonraker() {
      const selectedPrinter = this.printers.find((p) => p.id === this.selectedPrinterId)
      return !selectedPrinter || selectedPrinter.isAgentMoonraker()
    },
    isCloud() {
      return !this.selectedPrinterId
    },
    nothingFound() {
      return this.searchStateIsActive && !this.searchTimeoutId && !this.files.length
    },
    searchInProgress() {
      return this.searchStateIsActive && !!this.searchTimeoutId
    },
    maxFilesize() {
      return this.user.is_pro ? 500 : 50 // MB
    },
    maxTotalFilesize() {
      return this.user.is_pro ? 50 : 1 // GB
    },
    dropzoneOptions() {
      return {
        withCredentials: true,
        maxFilesize: this.maxFilesize,
        timeout: 60 * 60 * 1000, // For large files
        acceptedFiles: '.g,.gcode,.gco',
        url: urls.gcodeFiles(),
        headers: { 'X-CSRFToken': this.csrf },
      }
    },
  },

  async created() {
    this.csrf = getCsrfFromDocument()
    this.user = user()

    if (this.savedPath && this.savedPath.length >= 1) {
      this.parentFolder = this.savedPath.at(-1)
      this.path = this.savedPath.slice(0, this.savedPath.length - 1)
    } else {
      this.parentFolder = this.getRouteParam('parentFolder') || null
    }

    this.selectedPrinterId = Number(this.getRouteParam('printerId')) || null

    if (!this.isPopup) {
      this.$watch(
        () => this.$route.params,
        (toParams, previousParams) => {
          this.parentFolder = toParams.parentFolder || null
          this.selectedPrinterId = Number(this.getRouteParam('printerId')) || null
          this.fetchFilesAndFolders(true)
        }
      )
    }

    await this.fetchPrinters()
    this.fetchFilesAndFolders(true)
  },

  methods: {
    isPrinterBrowsable(printer) {
      return !(printer.isOffline() || !printer.isAgentVersionGte('2.3.0', '1.2.0'))
    },
    printerBrowsabilityText(printer) {
      return this.isPrinterBrowsable(printer)
        ? `${this.$i18next.t('Available to browse files')}`
        : `${this.$i18next.t('Unable to browse files')}`
    },
    toggleSelectAll() {
      if (this.allSelected) {
        this.$refs.gCodeFileStructure.unselectAll()
      } else {
        this.$refs.gCodeFileStructure.selectAll()
      }
    },
    onSelectFiles(items) {
      this.selectedFiles = items
    },
    onSelectFolders(items) {
      this.selectedFolders = items
    },
    moveSelectedItems() {
      this.activeItems = {
        files: Array.from(this.selectedFiles),
        folders: Array.from(this.selectedFolders),
      }
      this.$refs.moveModal.show()
    },
    deleteSelectedItems() {
      const selectedFolderIds = Array.from(this.selectedFolders)
      const selectedFileIds = Array.from(this.selectedFiles)
      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Are you sure?')}`,
        text: `${this.$i18next.t('Delete {name} item(s)? This action can not be undone.',{name:selectedFolderIds.length + selectedFileIds.length})}`,
        showCancelButton: true,
        confirmButtonText: `${this.$i18next.t('Yes')}`,
        cancelButtonText: `${this.$i18next.t('No')}`,
      }).then(async (userAction) => {
        if (userAction.isConfirmed) {
          try {
            if (selectedFolderIds.length)
              await axios.post(urls.gcodeFolderBulkDelete(), { folder_ids: selectedFolderIds })
            if (selectedFileIds.length)
              await axios.post(urls.gcodeFileBulkDelete(), { file_ids: selectedFileIds })
          } catch (err) {
            this.errorDialog(err, `${this.$i18next.t('Failed to delete files and folders')}`)
          } finally {
            this.fetchFilesAndFolders(true)
          }
        }
      })
    },
    switchToCloudStorage() {
      this.parentFolder = null
      this.path = []
      this.selectedPrinterId = null
      this.selectedPrinterComm = null
      if (this.isPopup) {
        this.fetchFilesAndFolders(true)
      } else {
        if (this.$route.path !== '/g_code_folders/cloud/') {
          this.$router.replace(`/g_code_folders/cloud/`)
        }
      }
    },
    switchToPrinterStorage(printer) {
      if (!this.isPrinterBrowsable(printer)) {
        this.$swal.Reject.fire({
          title: `${this.$i18next.t(`{name} isn't available for browsing files for one of the following reasons`,{name:printer.name})}:`,
          html: `<ul style="text-align: left">
            <li>${this.$i18next.t('{name} is powered off or not connected to the Internet',{name:printer.agentDisplayName()})}</li>
            <li>${this.$i18next.t('Printer is not connected to {name}',{name:printer.agentDisplayName()})}</li>
            <li>${this.$i18next.t("{brandName} for {name} plugin is outdated (you need version {version} or later)",{brandName:this.$syndicateText.brandName,name:printer.agentDisplayName(),version:printer.browsabilityMinPluginVersion()})}</li>
          </ul>`,
        })
        return
      }

      this.parentFolder = null
      this.path = []
      this.selectedPrinterId = printer.id
      this.selectedPrinterComm = null
      if (this.isPopup) {
        this.fetchFilesAndFolders(true)
      } else {
        if (Number(this.getRouteParam('printerId')) !== printer.id) {
          this.$router.replace(`/g_code_folders/local/${printer.id}/`)
        }
      }
    },
    getRouteParam(name) {
      return this.isPopup ? this.routeParams[name] : this.$route.params[name]
    },
    goBack() {
      if (!this.path.length) {
        return
      }
      this.parentFolder = this.path.pop()
      this.fetchFilesAndFolders(true)
    },
    resetFiles() {
      this.folders = []
      this.files = []
      this.$refs.gCodeFileStructure.unselectAll()
      this.noMoreFolders = false
      this.noMoreFiles = false
      this.currentFoldersPage = 1
      this.currentFilesPage = 1
    },
    async fetchPrinters() {
      let printers
      try {
        printers = await axios.get(urls.printers())
        printers = printers.data
      } catch (e) {
        console.error(e)
      }
      if (!printers) {
        return
      }
      printers = printers.map((p) => normalizedPrinter(p))
      // bring browsable printers at the top of the list
      printers = printers.sort(
        (a, b) => Number(this.isPrinterBrowsable(b)) - Number(this.isPrinterBrowsable(a))
      )
      this.printers = this.targetPrinter
        ? printers.filter((p) => p.id === this.targetPrinter.id)
        : printers
    },
    async fetchLocalFiles() {
      if (!this.selectedPrinterComm) {
        return
      }
      this.localFilesLoading = true
      const listPrinterLocalGCodes = this.isAgentMoonraker
        ? listPrinterLocalGCodesMoonraker
        : listPrinterLocalGCodesOctoPrint

      listPrinterLocalGCodes(
        this.selectedPrinterComm,
        this.parentFolder ? decodeURIComponent(this.parentFolder) : null,
        this.searchQuery
      ).then((result) => {
        this.localFilesLoading = false
        if (result) {
          const { folders, files } = result
          this.folders = folders
          this.files = files
        }
      })
    },
    async fetchFilesAndFolders(reset = false, printLastUploadedFile = false) {
      if (this.loading) {
        return
      }

      if (reset) {
        this.resetFiles()
      }

      // need to fetch local printer files
      if (this.selectedPrinterId) {
        if (!this.printers.find((p) => p.id === this.selectedPrinterId)) {
          this.$swal.Reject.fire({
            title: `${this.$i18next.t('Error')}`,
            text: `${this.$i18next.t(`Printer not found or unavailable`)}`,
          }).then(() => {
            if (this.isPopup && this.onClose) {
              this.onClose()
            } else {
              window.location.assign(`/g_code_folders/cloud/`)
            }
          })
        }

        this.localFilesLoading = true

        if (!this.selectedPrinterComm) {
          this.selectedPrinterComm = printerCommManager.getOrCreatePrinterComm(
            this.selectedPrinterId,
            urls.printerWebSocket(this.selectedPrinterId)
          )
          this.selectedPrinterComm.connect(this.fetchLocalFiles)
        } else {
          this.fetchLocalFiles()
        }
        return
      }

      if (this.searchQuery) {
        this.noMoreFolders = true
      }

      if (this.noMoreFolders && this.noMoreFiles) {
        return
      }

      this.loading = true
      let folders = []
      let files = []

      if (!this.noMoreFolders) {
        try {
          const params = {
            parent_folder: this.parentFolder || 'null',
            page: this.currentFoldersPage,
            page_size: PAGE_SIZE,
          }
          if (this.sortingValue.sorting.folderKey) {
            params.sorting = `${this.sortingValue.sorting.folderKey}_${this.sortingValue.direction.key}`
          }
          let response = await axios.get(urls.gcodeFolders(), { params })
          response = response.data
          this.noMoreFolders = response?.next === null
          folders = response?.results || []
        } catch (error) {
          this.loading = false
          this.errorDialog(error)
        }

        this.currentFoldersPage += 1
      }

      if (!this.noMoreFiles && folders.length < PAGE_SIZE) {
        try {
          let response = await axios.get(urls.gcodeFiles(), {
            // If cache is enabled, after renaming item on gcode page
            // and going back to files - gcode will have old name
            headers: {
              'Cache-Control': 'no-cache',
            },
            params: {
              // search is always global and we don't send parent_folder param at all in this case
              // if `parentFolder` is null, it means we are in root folder (server needs '' or 'null')
              parent_folder: this.searchQuery ? undefined : this.parentFolder || 'null',
              page: this.currentFilesPage,
              page_size: PAGE_SIZE,
              sorting: `${this.sortingValue.sorting.key}_${this.sortingValue.direction.key}`,
              q: this.searchQuery,
            },
          })
          response = response.data
          this.noMoreFiles = response?.next === null
          files = response?.results || []
        } catch (error) {
          this.loading = false
          this.errorDialog(error)
        }

        this.currentFilesPage += 1

        if (printLastUploadedFile) {
          try {
            let response = await axios.get(urls.gcodeFiles(), {
              params: {
                parent_folder: this.parentFolder || 'null',
                page_size: 1,
                sorting: `created_at_desc`,
              },
            })
            response = response.data
            if (response?.results && response.results[0]) {
              this.onPrintClicked(response.results[0])
            }
          } catch (error) {
            this.loading = false
            this.errorDialog(error)
          }
        }
      }

      this.folders.push(...folders.map((data) => normalizedGcodeFolder(data)))
      this.files.push(...files.map((data) => normalizedGcode(data)))
      this.loading = false
    },
    updateSearch(search) {
      clearTimeout(this.searchTimeoutId)
      this.searchTimeoutId = null

      this.searchStateIsActive = !!search
      if (!this.searchStateIsActive) {
        this.searchQuery = null
        this.fetchFilesAndFolders(true)
        return
      }

      this.searchTimeoutId = setTimeout(async () => {
        this.searchQuery = search
        this.fetchFilesAndFolders(true)
        this.searchTimeoutId = null
      }, SEARCH_API_CALL_DELAY)
    },
    addParentFolderParam(file, xhr, formData) {
      formData.append('filename', file.name)
      if (this.parentFolder !== null) {
        formData.append('parent_folder', this.parentFolder)
      }
    },
    gcodeUploadSuccess() {
      const printAfterUpload =
        this.targetPrinter &&
        this.$refs.gcodesDropzone.getAcceptedFiles().length === 1 &&
        this.$refs.gcodesDropzone.getRejectedFiles().length === 0

      this.$refs.gcodesDropzone.removeAllFiles()
      this.files = []
      this.fetchFilesAndFolders(true, printAfterUpload)
    },
    gcodeUploadError(file, message) {
      this.$swal.Reject.fire({
        html: `<p class="text-center">${message}</p>`,
      })
    },
    renameItem(item) {
      this.activeItem = item
      this.$refs.renameModal.show()
    },
    verifyItemRename(newName) {
      if (!this.activeItem.filename && this.folders.find((item) => item.name === newName)) {
        return `${this.$i18next.t('Folder with this name already exists')}`
      }
      return true
    },
    onItemRenamed(newName) {
      if (!this.activeItem) {
        return
      }
      const targetArr = this.activeItem.filename ? this.files : this.folders
      for (let i in targetArr) {
        if (targetArr[i].id !== this.activeItem.id) {
          continue
        } else if (this.activeItem.filename) {
          this.files[i].filename = newName
          break
        } else {
          this.folders[i].name = newName
          break
        }
      }
      this.activeItem = null
    },
    moveItem(item) {
      this.activeItem = item
      this.$refs.moveModal.show()
    },
    onItemMoved() {
      if (!this.activeItem && !this.activeItems) {
        return
      }
      this.activeItem = null
      this.activeItems = null
      this.fetchFilesAndFolders(true)
    },
    deleteItem(item) {
      this.activeItem = item
      this.$refs.deleteConfirmationModal.show()
    },
    onItemDeleted() {
      if (!this.activeItem) {
        return
      }
      const targetArr = this.activeItem.filename ? this.files : this.folders
      for (let i in targetArr) {
        if (targetArr[i].id !== this.activeItem.id) {
          continue
        } else if (this.activeItem.filename) {
          this.files.splice(i, 1)
          break
        } else {
          this.folders.splice(i, 1)
          break
        }
      }
      this.activeItem = null
    },
    createFolder() {
      this.$refs.newFolderModal.show()
    },
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'createFolder') {
        this.createFolder()
      }
    },
    verifyNewFolder(newFolderName) {
      if (this.folders.find((item) => item.name === newFolderName)) {
        return `${this.$i18next.t('Folder with this name already exists')}`
      }
      return true
    },
    onFolderCreated(newFolderId) {
      // this.openFolder({id: newFolderId})
      this.fetchFilesAndFolders(true)
    },
    openFolder(folder) {
      if (!this.isPopup) {
        if (this.selectedPrinterId) {
          this.$router.push(
            `/g_code_folders/local/${this.selectedPrinterId}/${encodeURIComponent(folder.path)}/`
          )
        } else {
          this.$router.push(`/g_code_folders/cloud/${folder.id}/`)
        }
      } else {
        this.path.push(this.parentFolder)
        this.parentFolder = String(folder.id)
        this.fetchFilesAndFolders(true)
      }
    },
    openFile(file) {
      if (!this.isPopup) {
        if (this.selectedPrinterId) {
          window.location.assign(
            `/g_code_files/local/${this.selectedPrinterId}/${encodeURIComponent(file.path)}/`
          )
        } else {
          window.location.assign(`/g_code_files/cloud/${file.id}/`)
        }
      } else {
        this.$emit(
          'openFile',
          this.selectedPrinterId ? encodeURIComponent(file.path) : file.id,
          this.selectedPrinterId,
          [...this.path, this.parentFolder]
        )
      }
    },
    onPrintClicked(gcode) {
      confirmPrint(gcode, this.targetPrinter).then(() => {
        sendToPrint({
          printer: this.targetPrinter,
          gcode: gcode,
          isCloud: this.isCloud,
          Swal: this.$swal,
          onCommandSent: () => {
            if (this.isPopup) {
              this.$bvModal.hide('b-modal-gcodes' + this.targetPrinter.id)
            }
          },
        })
      })
    },

    // Sorting
    onSortingUpdated(sortingValue) {
      this.sortingValue = sortingValue
      this.fetchFilesAndFolders(true)
    },
  },
}
</script>

<style lang="sass" scoped>
.upload-box
  margin-bottom: var(--gap-between-blocks) !important

.search-input
  height: 30px
  input
    background-color: var(--color-surface-secondary)
    border: var(--color-surface-secondary)

.notice-block
  border: 1px solid var(--color-divider)
  border-radius: var(--border-radius-md)
  display: flex
  align-items: center
  padding: 1rem 1.5rem
  margin-bottom: var(--gap-between-blocks)

  .message
    margin: 0
    margin-left: 1rem

.actions-with-selected-desktop
  display: flex
  align-items: center
  margin-right: 1rem
  .label
    cursor: pointer
  ::v-deep .custom-checkbox .custom-control-label::before
    border-radius: var(--border-radius-xs)
  @media (max-width: 576px)
    display: none
</style>
