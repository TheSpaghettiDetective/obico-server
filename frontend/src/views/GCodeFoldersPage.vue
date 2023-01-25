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
      <search-input class="search-input mr-3" @input="updateSearch"></search-input>
    </template>
    <template #topBarRight>
      <div class="d-flex">
        <!-- <a href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Upload G-Code">
          <i class="fas fa-file-upload"></i>
        </a> -->
        <a
          v-if="isCloud"
          href="#"
          class="btn shadow-none icon-btn d-none d-md-inline"
          title="Create folder"
          @click.prevent="createFolder"
        >
          <i class="fas fa-folder-plus"></i>
        </a>
        <!-- Storage dropdown -->
        <b-dropdown right no-caret toggle-class="icon-btn" class="order-md-2">
          <template #button-content>
            <i class="fas fa-server"></i>
          </template>
          <b-dropdown-text class="small text-secondary">STORAGE</b-dropdown-text>
          <b-dropdown-item @click="switchToCloudStorage">
            <div class="dropdown-group">
              <i
                class="fas fa-check text-primary"
                :style="{ visibility: isCloud ? 'visible' : 'hidden' }"
              ></i>
              <div class="text">
                <div class="title">Obico Cloud</div>
              </div>
            </div>
          </b-dropdown-item>
          <b-dropdown-item
            v-for="printer in printers"
            :key="printer.id"
            @click="() => switchToPrinterStorage(printer)"
          >
            <div class="dropdown-group">
              <i
                class="fas fa-check text-primary"
                :style="{ visibility: selectedPrinterId === printer.id ? 'visible' : 'hidden' }"
              ></i>
              <div class="text">
                <div class="title">{{ printer.name }}</div>
                <div
                  class="subtitle"
                  :class="[printer.isBrowsable() ? 'text-success' : 'text-warning']"
                >
                  {{ printer.browsabilityText() }}
                </div>
              </div>
            </div>
          </b-dropdown-item>
        </b-dropdown>
        <!-- Sorting / all actions for mobile -->
        <b-dropdown v-if="isCloud" right no-caret toggle-class="icon-btn" class="order-md-1">
          <template #button-content>
            <i class="fas fa-ellipsis-v d-md-none"></i>
            <i class="fas fa-sort-amount-down d-none d-md-block"></i>
          </template>
          <!-- <b-dropdown-item href="#" class="d-md-none">
            <i class="fas fa-file-upload"></i>Upload G-Code
          </b-dropdown-item> -->
          <b-dropdown-item class="d-md-none" @click="createFolder">
            <i class="fas fa-folder-plus"></i>Create Folder
          </b-dropdown-item>
          <b-dropdown-divider class="d-md-none"></b-dropdown-divider>
          <b-dropdown-text class="small text-secondary">ORDER</b-dropdown-text>
          <b-dropdown-item
            v-for="sortingOption in sorting.options"
            :key="`s_${sortingOption.id}`"
            @click="() => updateSorting(sortingOption)"
          >
            <i
              class="fas fa-check text-primary"
              :style="{ visibility: activeSorting.id === sortingOption.id ? 'visible' : 'hidden' }"
            ></i>
            {{ sortingOption.title }}
          </b-dropdown-item>
          <b-dropdown-divider />
          <b-dropdown-item
            v-for="sortingDirection in sorting.directions"
            :key="`d_${sortingDirection.id}`"
            @click="() => updateSorting(activeSorting, sortingDirection)"
          >
            <i
              class="fas fa-check text-primary"
              :style="{
                visibility:
                  activeSortingDirection.id === sortingDirection.id ? 'visible' : 'hidden',
              }"
            ></i>
            {{ sortingDirection.title }}
          </b-dropdown-item>
        </b-dropdown>
        <a
          v-if="onClose"
          href="#"
          class="btn shadow-none icon-btn d-inline order-4"
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
                <div>G-Code file (*.gcode, *.gco, or *.g) only.</div>
                <div>Up to {{ maxFilesize }} MB each file, {{ maxTotalFilesize }} GB total.</div>
              </div>
            </vue-dropzone>

            <g-code-file-structure
              :is-cloud="isCloud"
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
        :target-printer="targetPrinter"
        :scroll-container-id="scrollContainerId"
        :active-sorting="activeSorting"
        :active-sorting-direction="activeSortingDirection"
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
import { getLocalPref, setLocalPref } from '@src/lib/pref'
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
import { sendToPrint } from '@src/components/g-codes/sendToPrint'
import PrinterComm from '@src/lib/printer-comm'
import {
  listPrinterLocalGCodesOctoPrint,
  listPrinterLocalGCodesMoonraker,
} from '@src/lib/printer-local-comm'
import GCodeFileStructure from '@src/components/g-codes/GCodeFileStructure.vue'

// Waiting time (ms) before asking server for search results
const SEARCH_API_CALL_DELAY = 1000

const PAGE_SIZE = 24

const Sorting = {
  options: {
    name: {
      id: 1,
      title: 'Name',
      file_query: 'filename',
      folder_query: 'name',
    },
    size: {
      id: 2,
      title: 'Size',
      file_query: 'num_bytes',
    },
    created_at: {
      id: 3,
      title: 'Created',
      file_query: 'created_at',
      folder_query: 'created_at',
    },
  },
  directions: {
    asc: {
      id: 1,
      title: 'Ascending',
      query: 'asc',
    },
    desc: {
      id: 2,
      title: 'Descending',
      query: 'desc',
    },
  },
}
const LOCAL_PREF_NAMES = {
  sorting: 'gcode-folders-sorting-id',
  sortingDirection: 'gcode-folders-sorting-direction-id',
}
const getSortingById = (id) => {
  return Object.values(Sorting.options).find((s) => s.id === id)
}
const getSortingDirectionById = (id) => {
  return Object.values(Sorting.directions).find((s) => s.id === id)
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

      sorting: Sorting,
      activeSorting: getSortingById(
        getLocalPref(LOCAL_PREF_NAMES.sorting, Sorting.options.created_at.id)
      ),
      activeSortingDirection: getSortingDirectionById(
        getLocalPref(LOCAL_PREF_NAMES.sortingDirection, Sorting.directions.desc.id)
      ),

      searchQuery: null,
      searchStateIsActive: false,
      searchTimeoutId: null,

      activeItem: null,

      // local storage:
      printers: [],
      selectedPrinterId: undefined,
      selectedPrinterComm: undefined,
      localFilesLoading: false,
    }
  },

  computed: {
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
      if (!printer.isBrowsable()) {
        this.$swal.Reject.fire({
          title: `${printer.name} isn't available for browsing files for one of the following reasons:`,
          html: `<ul style="text-align: left">
            <li>${printer.agentDisplayName()} is powered off or not connected to the Internet</li>
            <li>Printer is not connected to ${printer.agentDisplayName()}</li>
            <li>Obico for ${printer.agentDisplayName()} plugin is outdated (you need version ${printer.browsabilityMinPluginVersion()} or later)</li>
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
      printers = printers.sort((a, b) => Number(b.isBrowsable()) - Number(a.isBrowsable()))
      this.printers = this.targetPrinter
        ? printers.filter((p) => p.id === this.targetPrinter.id)
        : printers
    },
    async fetchLocalFiles() {
      if (!this.selectedPrinterComm) {
        return
      }
      this.localFilesLoading = true
      const isAgentMoonraker = this.printers
        .find((p) => p.id === this.selectedPrinterId)
        .isAgentMoonraker()
      const listPrinterLocalGCodes = isAgentMoonraker
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
    async fetchFilesAndFolders(reset = false) {
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
            title: 'Error',
            text: `Printer not found or unavailable`,
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
          this.selectedPrinterComm = PrinterComm(
            this.selectedPrinterId,
            urls.printerWebSocket(this.selectedPrinterId),
            (data) => {},
            (printerStatus) => {}
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
          let response = await axios.get(urls.gcodeFolders(), {
            params: {
              parent_folder: this.parentFolder || 'null',
              page: this.currentFoldersPage,
              page_size: PAGE_SIZE,
              sorting: `${this.activeSorting.folder_query}_${this.activeSortingDirection.query}`,
            },
          })
          response = response.data
          this.noMoreFolders = response?.next === null
          folders = response?.results || []
        } catch (error) {
          this.loading = false
          this._showErrorPopup(error)
        }

        this.folders.push(...folders.map((data) => normalizedGcodeFolder(data)))
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
              parent_folder: this.parentFolder || 'null',
              page: this.currentFilesPage,
              page_size: PAGE_SIZE,
              sorting: `${this.activeSorting.file_query}_${this.activeSortingDirection.query}`,
              q: this.searchQuery,
            },
          })
          response = response.data
          this.noMoreFiles = response?.next === null
          files = response?.results || []
        } catch (error) {
          this.loading = false
          this._showErrorPopup(error)
        }

        this.files.push(...files.map((data) => normalizedGcode(data)))
        this.currentFilesPage += 1
      }

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
    updateSorting(newSortingOption, newSortingDirection = this.activeSortingDirection) {
      let sortingChanged = false

      if (this.activeSorting.id !== newSortingOption.id) {
        this.activeSorting = newSortingOption
        setLocalPref(LOCAL_PREF_NAMES.sorting, newSortingOption.id)
        sortingChanged = true
      }

      if (this.activeSortingDirection.id !== newSortingDirection.id) {
        this.activeSortingDirection = newSortingDirection
        setLocalPref(LOCAL_PREF_NAMES.sortingDirection, newSortingDirection.id)
        sortingChanged = true
      }

      if (sortingChanged) {
        this.fetchFilesAndFolders(true)
      }
    },
    addParentFolderParam(file, xhr, formData) {
      formData.append('filename', file.name)
      if (this.parentFolder !== null) {
        formData.append('parent_folder', this.parentFolder)
      }
    },
    gcodeUploadSuccess() {
      this.$refs.gcodesDropzone.removeAllFiles()
      this.files = []
      this.fetchFilesAndFolders(true)
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
        return 'Folder with this name already exists'
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
      if (!this.activeItem) {
        return
      }
      this.activeItem = null
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
    verifyNewFolder(newFolderName) {
      if (this.folders.find((item) => item.name === newFolderName)) {
        return 'Folder with this name already exists'
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
      sendToPrint({
        printerId: this.targetPrinter.id,
        gcode: gcode,
        isCloud: this.isCloud,
        isAgentMoonraker: this.targetPrinter.isAgentMoonraker(),
        Swal: this.$swal,
        onCommandSent: () => {
          if (this.isPopup) {
            this.$bvModal.hide('b-modal-gcodes')
          }
        },
      })
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

.dropdown-group
  display: flex
  align-items: center
  .text
    display: flex
    flex-direction: column
    .subtitle
      font-size: 0.75rem
</style>
