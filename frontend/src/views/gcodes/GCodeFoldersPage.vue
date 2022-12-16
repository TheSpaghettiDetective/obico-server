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
      <div>
        <!-- <a href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Upload G-Code">
          <i class="fas fa-file-upload"></i>
        </a> -->
        <a @click.prevent="createFolder" href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Create folder">
          <i class="fas fa-folder-plus"></i>
        </a>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
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
        <a v-if="onClose" @click.prevent="onClose" href="#" class="btn shadow-none icon-btn d-inline" title="Close">
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
              <div class="header-panel">
                <div class="text">Name</div>
                <div class="text">Size</div>
                <div class="text">Created</div>
                <div class="text">Last printed</div>
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
                      <div class="created">{{ item.created_at.fromNow() }}</div>
                      <div></div>
                    </div>
                    <div>
                      <b-dropdown right no-caret toggle-class="icon-btn">
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
                  <div v-for="item in files" :key="`gcode_${item.id}`" class="item" @click="(event) => openFile(event, item)">
                    <div class="item-info">
                      <div class="filename">
                        <i class="fas fa-file-code mr-1"></i>
                        {{ item.filename }}
                      </div>
                      <div class="size">{{ item.filesize }}</div>
                      <div class="uploaded">{{ item.created_at.fromNow() }}</div>
                      <div class="last-printed">
                        <span v-if="!item.print_set.length">No prints yet</span>
                        <span v-else-if="item.last_printed_at">{{ item.last_printed_at.fromNow() }}</span>
                        <div v-else>
                          <span>Printing...</span>
                          <!-- <b-spinner small class="ml-1" /> -->
                        </div>
                        <div
                          v-if="item.last_printed_at"
                          class="circle-indicator"
                          :class="item.last_print_result"
                        ></div>
                      </div>
                    </div>
                    <div>
                      <b-dropdown right no-caret toggle-class="icon-btn">
                        <template #button-content>
                          <i class="fas fa-ellipsis-v"></i>
                        </template>
                        <b-dropdown-item v-if="targetPrinter" @click="(event) => onPrintClicked(event, item)">
                          <span class="text-primary">
                            <i class="fas fa-play-circle"></i>Print on {{ targetPrinter.name }}
                          </span>
                        </b-dropdown-item>
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

                <!-- Pagination -->
                <mugen-scroll
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

                <!-- Placeholders -->
                <div v-if="isFolderEmpty" class="placeholder text-secondary">
                  <span>Nothing here yet</span>
                </div>
                <div v-else-if="nothingFound" class="placeholder text-secondary">
                  <span>Nothing found</span>
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
import { normalizedGcode, normalizedGcodeFolder } from '@src/lib/normalizers'
import { user } from '@src/lib/page_context'
import SearchInput from '@src/components/SearchInput.vue'
import MugenScroll from 'vue-mugen-scroll'
import { getCsrfFromDocument, wasElementClicked } from '@src/lib/utils'
import NewFolderModal from './NewFolderModal.vue'
import RenameModal from './RenameModal.vue'
import DeleteConfirmationModal from './DeleteConfirmationModal.vue'
import { sendToPrint } from './sendToPrint'

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
    }
  },

  created() {
    this.csrf = getCsrfFromDocument()
    this.user = user()

    if (!this.isPopup) {
      this.parentFolder = this.$route.params.parentFolder || null
      this.$watch(
        () => this.$route.params,
        (toParams, previousParams) => {
          this.parentFolder = toParams.parentFolder || null
          this.fetchFilesAndFolders(true)
        }
      )
    } else {
      this.parentFolder = null
    }

    this.fetchFilesAndFolders(true)
  },

  computed: {
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
    goBack() {
      if (!this.path.length) {
        return
      }
      this.parentFolder = this.path.pop()
      this.fetchFilesAndFolders(true)
    },
    async fetchFilesAndFolders(reset = false) {
      if (reset) {
        this.folders = []
        this.files = []
        this.noMoreFolders = false
        this.noMoreFiles = false
        this.currentFoldersPage = 1
        this.currentFilesPage = 1
      }

      if (this.searchQuery) {
        this.noMoreFolders = true
      }

      if (this.noMoreFolders && this.noMoreFiles) return

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
      if (!this.activeItem) return
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
      if (!this.activeItem) return
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
      if (wasElementClicked(event, 'dropdown-item')) return

      if (!this.isPopup) {
        this.$router.push(`/g_code_folders/${folder.id}/`)
      } else {
        this.path.push(this.parentFolder)
        this.parentFolder = folder.id
        this.fetchFilesAndFolders(true)
      }
    },
    openFile(event, file) {
      if (wasElementClicked(event, 'dropdown-item')) return

      if (!this.isPopup) {
        window.location.assign(`/g_code_files/${file.id}/`)
      } else {
        this.$emit('openFile', file.id)
      }
    },
    onPrintClicked(event, gcode) {
      sendToPrint(this.targetPrinter.id, this.targetPrinter.name, gcode, this.$swal, {
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
  margin-bottom: var(--gap-between-blocks)

.search-input
  height: 30px
  input
    background-color: var(--color-surface-secondary)
    border: var(--color-surface-secondary)

.gcodes-wrapper
  background-color: var(--color-surface-secondary)
  padding: 1em 2em
  border-radius: var(--border-radius-lg)
  margin-top: 2rem

.header-panel
  display: flex
  padding: 1em calc(1em + 30px) 1em 1em
  border-bottom: 1px solid var(--color-divider)
  font-weight: bold

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
</style>
