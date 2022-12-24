<template>
  <layout :isPopup="isPopup">

    <!-- Tob bar -->
    <template v-slot:topBarLeft>
      <a v-if="isPopup && parentFolder !== null" @click.prevent="goBack" href="#" class="btn shadow-none icon-btn d-inline" title="Go Back">
        <i class="fas fa-chevron-left"></i>
      </a>
      <search-input @input="updateSearch" class="search-input mr-3"></search-input>
    </template>
    <template v-slot:topBarRight>
      <div class="d-flex">
        <!-- <a href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Upload G-Code">
          <i class="fas fa-file-upload"></i>
        </a> -->
        <a v-if="isCloud" @click.prevent="createFolder" href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Create folder">
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
              <i class="fas fa-check text-primary" :style="{visibility: isCloud ? 'visible' : 'hidden'}"></i>
              <div class="text">
                <div class="title">Obico Cloud</div>
              </div>
            </div>
          </b-dropdown-item>
          <b-dropdown-item v-for="printer in printers" :key="printer.id" @click="() => switchToPrinterStorage(printer)">
            <div class="dropdown-group">
              <i class="fas fa-check text-primary" :style="{visibility: selectedPrinterId === printer.id ? 'visible' : 'hidden'}"></i>
              <div class="text">
                <div class="title">{{ printer.name }}</div>
                <div
                  class="subtitle"
                  :class="{
                    'text-secondary': printer.storageAvailability.key === 'offline',
                    'text-success': printer.storageAvailability.key === 'online',
                    'text-warning': printer.storageAvailability.key === 'plugin_outdated',
                  }"
                >
                  {{ printer.storageAvailability.text }}
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
            <i class="fas fa-check text-primary" :style="{visibility: activeSorting.id === sortingOption.id ? 'visible' : 'hidden'}"></i>
            {{ sortingOption.title }}
          </b-dropdown-item>
          <b-dropdown-divider />
          <b-dropdown-item
            v-for="sortingDirection in sorting.directions"
            :key="`d_${sortingDirection.id}`"
            @click="() => updateSorting(activeSorting, sortingDirection)"
          >
            <i class="fas fa-check text-primary" :style="{visibility: activeSortingDirection.id === sortingDirection.id ? 'visible' : 'hidden'}"></i>
            {{ sortingDirection.title }}
          </b-dropdown-item>
        </b-dropdown>
        <a v-if="onClose" @click.prevent="onClose" href="#" class="btn shadow-none icon-btn d-inline order-4" title="Close">
          <i class="fas fa-times text-danger"></i>
        </a>
      </div>
    </template>

    <!-- Page content -->
    <template v-slot:content>
      <b-container>
        <b-row>
          <b-col>
            <vue-dropzone
              v-if="isCloud"
              class="upload-box"
              id="dropzone"
              :options="dropzoneOptions"
              :useCustomSlot="true"
              @vdropzone-queue-complete="gcodeUploadSuccess"
              @vdropzone-error="gcodeUploadError"
              @vdropzone-sending="addParentFolderParam"
              ref="gcodesDropzone"
            >
              <div class="dz-message needsclick">
                <i class="fas fa-upload fa-2x"></i> <br>
                <div>G-Code file (*.gcode, *.gco, or *.g) only.</div>
                <div>Up to {{maxFilesize}} MB each file, {{maxTotalFilesize}} GB total.</div>
              </div>
            </vue-dropzone>

            <div class="gcodes-wrapper">
              <div class="header-panel" :class="{'without-action-buttons': !isCloud && !targetPrinter}">
                <div class="text">Name</div>
                <div class="text">Size</div>
                <div class="text">Created</div>
                <div class="text" v-if="isCloud">Last printed</div>
              </div>

              <div class="gcode-items-wrapper">
                <!-- Folders -->
                <div v-if="!searchStateIsActive">
                  <div v-for="item in folders" :key="`folder_${item.id}`" class="item folder" @click="(event) => openFolder(event, item)">
                    <div class="item-info">
                      <div class="filename">
                        <i class="fas fa-folder mr-1"></i>
                        {{ item.name }}
                      </div>
                      <div class="size">{{ item.numItems }} item(s)</div>
                      <div class="created">{{ item.created_at ? item.created_at.fromNow() : '-' }}</div>
                      <div class="d-none d-md-block" v-if="isCloud">-</div>
                    </div>
                    <div v-if="isCloud">
                      <b-dropdown right no-caret toggle-class="icon-btn py-0">
                        <template #button-content>
                          <i class="fas fa-ellipsis-v"></i>
                        </template>
                        <b-dropdown-item @click="renameItem(item)">
                          <i class="fas fa-edit"></i>Rename
                        </b-dropdown-item>
                        <!-- <b-dropdown-item>
                          <i class="fas fa-arrows-alt"></i>Move
                        </b-dropdown-item> -->
                        <b-dropdown-item @click="deleteItem(item)">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </b-dropdown-item>
                      </b-dropdown>
                    </div>
                  </div>
                </div>

                <!-- Files -->
                <div v-if="!searchInProgress">
                  <div v-for="(item, key) in files" :key="`gcode_${key}`" class="item" @click="(event) => openFile(event, item)">
                    <div class="item-info">
                      <div class="filename">
                        <i class="fas fa-file-code mr-1"></i>
                        {{ item.filename }}
                      </div>
                      <div class="size">{{ item.filesize }}</div>
                      <div class="uploaded">{{ item.created_at ? item.created_at.fromNow() : '-' }}</div>
                      <div class="last-printed" v-if="isCloud">
                        <span v-if="!item.print_set">-</span>
                        <span v-else-if="!item.print_set.length">No prints yet</span>
                        <span v-else-if="item.last_print">{{ item.last_print.ended_at ? item.last_print.ended_at.fromNow() : 'Printing...' }}</span>
                        <div
                          v-if="item.last_print_result"
                          class="circle-indicator"
                          :class="item.last_print_result"
                        ></div>
                      </div>
                    </div>
                    <div v-if="isCloud || targetPrinter">
                      <b-dropdown right no-caret toggle-class="icon-btn py-0">
                        <template #button-content>
                          <i class="fas fa-ellipsis-v"></i>
                        </template>
                        <b-dropdown-item v-if="targetPrinter" @click="(event) => onPrintClicked(event, item)">
                          <span class="text-primary">
                            <i class="fas fa-play-circle"></i>Print on {{ targetPrinter.name }}
                          </span>
                        </b-dropdown-item>
                        <b-dropdown-item v-if="isCloud" @click="renameItem(item)">
                          <i class="fas fa-edit"></i>Rename
                        </b-dropdown-item>
                        <!-- <b-dropdown-item>
                          <i class="fas fa-arrows-alt"></i>Move
                        </b-dropdown-item> -->
                        <b-dropdown-item v-if="isCloud" @click="deleteItem(item)">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </b-dropdown-item>
                      </b-dropdown>
                    </div>
                  </div>
                </div>

                <!-- Pagination -->
                <mugen-scroll
                  v-if="isCloud"
                  :v-show="!isFolderEmpty"
                  :handler="fetchFilesAndFolders"
                  :should-handle="!loading"
                  class="text-center"
                  :scroll-container="scrollContainerId"
                >
                  <div v-if="!noMoreFolders || !noMoreFiles || searchInProgress" class="py-5">
                    <b-spinner label="Loading..." />
                  </div>
                </mugen-scroll>

                <div v-if="!isCloud && (localFilesLoading || searchInProgress)" class="text-center py-5">
                  <b-spinner label="Loading..." />
                </div>
                <div v-else>
                  <!-- Placeholders -->
                  <div v-if="isFolderEmpty" class="placeholder text-secondary">
                    <span>Nothing here yet</span>
                  </div>
                  <div v-else-if="nothingFound" class="placeholder text-secondary">
                    <span>Nothing found</span>
                  </div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
      <rename-modal
        :item="activeItem"
        @renamed="onItemRenamed"
        :preConfirm="verifyItemRename"
        ref="renameModal"
      />
      <delete-confirmation-modal
        :item="activeItem"
        @deleted="onItemDeleted"
        ref="deleteConfirmationModal"
      />
      <new-folder-modal
        @created="onFolderCreated"
        :preConfirm="verifyNewFolder"
        :parentFolderId="parentFolder ? parentFolder.id : null"
        ref="newFolderModal"
      />
    </template>
  </layout>
</template>

<script>
import Layout from '@src/components/Layout.vue'
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedGcode, normalizedGcodeFolder, normalizedPrinter } from '@src/lib/normalizers'
import { user } from '@src/lib/page_context'
import SearchInput from '@src/components/SearchInput.vue'
import MugenScroll from 'vue-mugen-scroll'
import { getCsrfFromDocument, wasElementClicked } from '@src/lib/utils'
import NewFolderModal from './NewFolderModal.vue'
import RenameModal from './RenameModal.vue'
import DeleteConfirmationModal from './DeleteConfirmationModal.vue'
import { sendToPrint } from './sendToPrint'
import PrinterComm from '@src/lib/printer_comm'
import { listFiles, getPrinterStorageAvailability } from './localFiles'

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

export default {
  name: 'GCodeFoldersPage',

  components: {
    Layout,
    SearchInput,
    vueDropzone: vue2Dropzone,
    MugenScroll,
    RenameModal,
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
      required: false,
    },
    scrollContainerId: {
      type: String,
      default: null,
    },
    targetPrinter: {
      type: Object,
      required: false,
    },
    savedPath: {
      type: Array,
      required: false,
    },
    routeParams: {
      type: Object,
      default: () => {
        return {
          printerId: null,
          parentFolder: null,
        }
      }
    }
  },

  data() {
    return {
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
      activeSorting: Sorting.options.created_at,
      activeSortingDirection: Sorting.directions.desc,

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

  computed: {
    isCloud() {
      return !this.selectedPrinterId
    },
    isFolderEmpty() {
      return !this.searchStateIsActive && !this.loading && !this.files.length && !this.folders.length
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
      if (printer.storageAvailability.rejectMessage) {
        this.$swal.Reject.fire({
          text: printer.storageAvailability.rejectMessage
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
      printers = printers.map(p => normalizedPrinter(p))
      printers = printers.map(p => ({...p, storageAvailability: getPrinterStorageAvailability(p)}))
      this.printers = this.targetPrinter ? printers.filter(p => p.id === this.targetPrinter.id) : printers
    },
    async fetchLocalFiles() {
      if (!this.selectedPrinterComm) {
        return
      }
      this.localFilesLoading = true
      listFiles(this.selectedPrinterComm, {
        query: this.searchQuery,
        path: this.parentFolder ? decodeURIComponent(this.parentFolder) : null,
        onRequestEnd: (result) => {
          this.localFilesLoading = false
          if (result) {
            const { folders, files } = result
            this.folders = folders
            this.files = files
          }
        },
      })
    },
    async fetchFilesAndFolders(reset = false) {
      if (this.loading) {
        return
      }

      if (reset) {
        this.resetFiles()
      }

      if (this.selectedPrinterId) {
        if (!this.printers.find(p => p.id === this.selectedPrinterId)) {
          this.$swal.Reject.fire({
            title: 'Error',
            text: `Printer not found or unavailable`,
          })
          .then(() => {
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
          let response = await axios.get(urls.gcodeFolders({
            parentFolder: this.parentFolder,
            page: this.currentFoldersPage,
            pageSize: PAGE_SIZE,
            sortingOption: this.activeSorting.folder_query,
            sortingDirection: this.activeSortingDirection.query,
          }))
          response = response.data
          this.noMoreFolders = response?.next === null
          folders = response?.results || []
        } catch (e) {
          this.loading = false
          this.$swal.Reject.fire({
            title: 'Error',
            text: e.message,
          })
          console.error(e)
        }

        this.folders.push(...folders.map(data => normalizedGcodeFolder(data)))
        this.currentFoldersPage += 1
      }

      if (!this.noMoreFiles && folders.length < PAGE_SIZE) {
        try {
          let response = await axios.get(urls.gcodeFiles({
              parentFolder: this.parentFolder,
              page: this.currentFilesPage,
              pageSize: PAGE_SIZE,
              sortingOption: this.activeSorting.file_query,
              sortingDirection: this.activeSortingDirection.query,
              query: this.searchQuery,
            }),
            {
              // If cache is enabled, after renaming item on gcode page
              // and going back to files - gcode will have old name
              headers: {
                'Cache-Control': 'no-cache',
              }
            }
          )
          response = response.data
          this.noMoreFiles = response?.next === null
          files = response?.results || []
        } catch (e) {
          this.loading = false
          this.$swal.Reject.fire({
            title: 'Error',
            text: e.message,
          })
          console.error(e)
        }

        this.files.push(...files.map(data => normalizedGcode(data)))
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
        sortingChanged = true
      }

      if (this.activeSortingDirection.id !== newSortingDirection.id) {
        this.activeSortingDirection = newSortingDirection
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
        html: `<p class="text-center">${message}</p>`})
    },
    renameItem(item) {
      this.activeItem = item
      this.$refs.renameModal.show()
    },
    verifyItemRename(newName) {
      if (!this.activeItem.filename && this.folders.find(item => item.name === newName)) {
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
      if (this.folders.find(item => item.name === newFolderName)) {
        return 'Folder with this name already exists'
      }
      return true
    },
    onFolderCreated(newFolderId) {
      // this.openFolder({id: newFolderId})
      this.fetchFilesAndFolders(true)
    },
    openFolder(event, folder) {
      if (wasElementClicked(event, 'dropdown-item')) {
        return
      }

      if (!this.isPopup) {
        if (this.selectedPrinterId) {
          this.$router.push(`/g_code_folders/local/${this.selectedPrinterId}/${encodeURIComponent(folder.path)}/`)
        } else {
          this.$router.push(`/g_code_folders/cloud/${folder.id}/`)
        }
      } else {
        this.path.push(this.parentFolder)
        this.parentFolder = folder.id
        this.fetchFilesAndFolders(true)
      }
    },
    openFile(event, file) {
      if (wasElementClicked(event, 'dropdown-item')) {
        return
      }
      if (!this.isPopup) {
        if (this.selectedPrinterId) {
          window.location.assign(`/g_code_files/local/${this.selectedPrinterId}/${encodeURIComponent(file.path)}/`)
        } else {
          window.location.assign(`/g_code_files/cloud/${file.id}/`)
        }
      } else {
        this.$emit('openFile', this.selectedPrinterId ? encodeURIComponent(file.path) : file.id, this.selectedPrinterId, [...this.path, this.parentFolder])
      }
    },
    onPrintClicked(event, gcode) {
      sendToPrint({
        printerId: this.targetPrinter.id,
        gcode: gcode,
        isCloud: this.isCloud,
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

.gcodes-wrapper
  background-color: var(--color-surface-secondary)
  padding: 1em 2em
  border-radius: var(--border-radius-lg)

.header-panel
  display: flex
  padding: 1em calc(1em + 30px) 1em 1em
  border-bottom: 1px solid var(--color-divider)
  font-weight: bold
  &.without-action-buttons
    padding-right: 1em

  & > div
    flex: 1
    display: flex
    justify-content: space-between
    margin-left: 30px
    align-items: center
    font-size: 1rem

    &:first-child
      margin-left: 0
      flex: 3

  @media (max-width: 768px)
    &
      display: none

.gcode-items-wrapper
  .item
    display: flex
    align-items: center
    padding: .6em 1em
    border-bottom: 1px solid var(--color-divider-muted)

    &:not(.folder)
      &:last-child
        border-bottom: none

    &:hover
      cursor: pointer
      background-color: var(--color-hover)

    .item-info
      display: flex
      width: 100%
      overflow: hidden
      flex: 1
      font-size: 0.875rem
      color: var(--color-text-secondary)

      & > div
        flex: 1
        margin-left: 30px

        &:first-child
          font-size: 1rem
          color: var(--color-text-primary)
          margin-left: 0

      .filename
        text-overflow: ellipsis
        overflow: hidden
        white-space: nowrap
        width: 100%
        flex: 3

    .remove-button
      width: 30px
      height: 30px
      text-align: center
      line-height: 30px
      border-radius: 50%
      transition: background-color .2s ease-out

      &:hover
        background-color: var(--color-danger)
        color: var(--color-on-primary)
        cursor: pointer

    @media (max-width: 768px)
      &
        margin: 0 -16px

      .item-info
        flex-direction: column
        align-items: flex-start

        & > div
          margin-left: 0

        .size::before
          content: "Size: "
        .uploaded::before
          content: "Uploaded: "
        .created::before
          content: "Created: "
        .last-printed::before
          content: "Last print: "

.circle-indicator
  --size: 6px
  width: var(--size)
  height: var(--size)
  border-radius: var(--size)
  display: inline-block
  margin-left: 5px
  position: relative
  bottom: 1px
  background: var(--color-text-secondary)
  &.cancelled
    background: var(--color-danger)
  &.finished
    background: var(--color-success)

.placeholder
  margin: 5rem 0
  text-align: center
  &.text-secondary *
    color: var(--color-text-secondary)

.dropdown-group
  display: flex
  align-items: center
  .text
    display: flex
    flex-direction: column
    .subtitle
      font-size: 0.75rem
</style>
