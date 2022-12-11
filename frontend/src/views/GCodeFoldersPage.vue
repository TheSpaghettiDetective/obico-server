<template>
  <layout>

    <!-- Tob bar -->
    <template v-slot:topBarLeft>
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
            v-for="sortingOption in sortingOptions"
            :key="`s_${sortingOption}`"
            @click="() => activeSorting = sortingOption"
          >
            <i class="fas fa-check text-primary" :style="{visibility: activeSorting === sortingOption ? 'visible' : 'hidden'}"></i>
            {{ sortingTitle[sortingOption] }}
          </b-dropdown-item>
          <b-dropdown-divider />
          <b-dropdown-item
            v-for="sortingDirection in sortingDirections"
            :key="`d_${sortingDirection}`"
            @click="() => activeSortingDirection = sortingDirection"
          >
            <i class="fas fa-check text-primary" :style="{visibility: activeSortingDirection === sortingDirection ? 'visible' : 'hidden'}"></i>
            {{ sortingDirectionTitle[sortingDirection] }}
          </b-dropdown-item>
        </b-dropdown>
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
              <div class="sorting-panel">
                <div
                  class="sorting-option"
                  :class="{'active': activeSorting === sortingOptions.NAME}"
                  @click="updateSorting(sortingOptions.NAME)"
                >
                  <span class="text">Name</span>
                  <div class="direction">
                    <i class="fas fa-arrow-down" v-if="activeSorting === sortingOptions.NAME && activeSortingDirection === sortingDirections.DESC"></i>
                    <i class="fas fa-arrow-up" v-else></i>
                  </div>
                </div>
                <div
                  class="sorting-option"
                  :class="{'active': activeSorting === sortingOptions.SIZE}"
                  @click="updateSorting(sortingOptions.SIZE)"
                >
                  <span class="text">Size</span>
                  <div class="direction">
                    <i class="fas fa-arrow-down" v-if="activeSorting === sortingOptions.SIZE && activeSortingDirection === sortingDirections.DESC"></i>
                    <i class="fas fa-arrow-up" v-else></i>
                  </div>
                </div>
                <div
                  class="sorting-option"
                  :class="{'active': activeSorting === sortingOptions.CREATED}"
                  @click="updateSorting(sortingOptions.CREATED)"
                >
                  <span class="text">Created</span>
                  <div class="direction">
                    <i class="fas fa-arrow-down" v-if="activeSorting === sortingOptions.CREATED && activeSortingDirection === sortingDirections.DESC"></i>
                    <i class="fas fa-arrow-up" v-else></i>
                  </div>
                </div>
                <div
                  class="sorting-option"
                  :class="{'active': activeSorting === sortingOptions.LAST_PRINTED}"
                  @click="updateSorting(sortingOptions.LAST_PRINTED)"
                >
                  <span class="text">Last printed</span>
                  <div class="direction">
                    <i class="fas fa-arrow-down" v-if="activeSorting === sortingOptions.LAST_PRINTED && activeSortingDirection === sortingDirections.DESC"></i>
                    <i class="fas fa-arrow-up" v-else></i>
                  </div>
                </div>
              </div>

              <div class="gcode-items-wrapper">
                <!-- Folders -->
                <div v-if="!searchStateIsActive && !loading">
                  <div v-for="item in foldersToShow" :key="`folder_${item.id}`" class="item folder" @click="openFolder(item)">
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
                        <b-dropdown-item @click="renameItem(item.id, item.name, 'folder')">
                          <i class="fas fa-edit"></i>Rename
                        </b-dropdown-item>
                        <!-- <b-dropdown-item>
                          <i class="fas fa-arrows-alt"></i>Move
                        </b-dropdown-item> -->
                        <b-dropdown-item @click="deleteItem(item.id, 'folder')">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </b-dropdown-item>
                      </b-dropdown>
                    </div>
                  </div>
                </div>

                <!-- Gcodes -->
                <div  v-if="!loading">
                  <div v-for="item in gcodesToShow" :key="`gcode_${item.id}`" class="item" @click="openFile(item)">
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
                        <!-- <b-dropdown-item>
                          <span class="text-primary">
                            <i class="fas fa-play-circle"></i>Print
                          </span>
                        </b-dropdown-item> -->
                        <b-dropdown-item @click="renameItem(item.id, item.filename, 'file')">
                          <i class="fas fa-edit"></i>Rename
                        </b-dropdown-item>
                        <!-- <b-dropdown-item>
                          <i class="fas fa-arrows-alt"></i>Move
                        </b-dropdown-item> -->
                        <b-dropdown-item @click="deleteItem(item.id, 'file')">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </b-dropdown-item>
                      </b-dropdown>
                    </div>
                  </div>
                </div>

                <!-- Placeholders -->
                <div v-if="loading || (searchStateIsActive && searchTimeoutId)" class="placeholder">
                  <b-spinner />
                </div>
                <div v-else-if="!searchStateIsActive && !gcodesToShow.length && !foldersToShow.length" class="placeholder text-secondary">
                  <span>Nothing here yet</span>
                </div>
                <div v-else-if="searchStateIsActive && !searchTimeoutId && !gcodesToShow.length" class="placeholder text-secondary">
                  <span>Nothing found</span>
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
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedGcode, normalizedGcodeFolder } from '@src/lib/normalizers'
import { user } from '@src/lib/page_context'
import SearchInput from '@src/components/SearchInput.vue'

// Waiting time (ms) before asking server for search results
const SEARCH_API_CALL_DELAY = 1000

// Sorting consts
const SORTING_OPTIONS = {
  NAME: 1,
  SIZE: 2,
  CREATED: 3,
  LAST_PRINTED: 4,
}
const SORTING_OPTIONS_TITLE = {
  [SORTING_OPTIONS.NAME]: 'Name',
  [SORTING_OPTIONS.SIZE]: 'Size',
  [SORTING_OPTIONS.CREATED]: 'Created',
  [SORTING_OPTIONS.LAST_PRINTED]: 'Last Printed',
}
const SORTING_DIRECTIONS = {
  ASC: 1,
  DESC: -1,
}
const SORTING_DIRECTION_TITLE = {
  [SORTING_DIRECTIONS.ASC]: 'Ascending',
  [SORTING_DIRECTIONS.DESC]: 'Descending',
}

export default {
  name: 'GCodesPage',

  components: {
    Layout,
    SearchInput,
    vueDropzone: vue2Dropzone,
  },

  props: {
    csrf: {
      type: String,
      requeired: true,
    },
  },

  data() {
    return {
      user: null,
      loading: false,
      parentFolder: null,
      gcodes: [],
      folders: [],

      activeSorting: SORTING_OPTIONS.CREATED,
      activeSortingDirection: SORTING_DIRECTIONS.DESC,
      sortingOptions: SORTING_OPTIONS,
      sortingTitle: SORTING_OPTIONS_TITLE,
      sortingDirectionTitle: SORTING_DIRECTION_TITLE,
      sortingDirections: SORTING_DIRECTIONS,

      searchStateIsActive: false,
      searchResultGcodes: [],
      searchTimeoutId: null,
    }
  },

  created() {
    this.user = user()
    this.parentFolder = this.$route.params.parentFolder || null
    this.fetchFilesAndFolders()

    this.$watch(
      () => this.$route.params,
      (toParams, previousParams) => {
        this.parentFolder = toParams.parentFolder || null
        this.fetchFilesAndFolders()
      }
    )
  },

  computed: {
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
    gcodesToShow() {
      let gcodes = this.gcodes

      if (this.searchStateIsActive) {
        gcodes = this.searchResultGcodes
      }

      if (!gcodes || this.searchTimeoutId) {
        return []
      }

      const sortDirection = this.activeSortingDirection

      switch (this.activeSorting) {
        case SORTING_OPTIONS.NAME:
          gcodes.sort(function(a, b) {
            var filenameA = a.filename.toUpperCase() // ignore upper and lowercase
            var filenameB = b.filename.toUpperCase() // ignore upper and lowercase
            if (filenameA < filenameB) {
              return sortDirection === SORTING_DIRECTIONS.ASC ? -1 : 1
            }
            if (filenameA > filenameB) {
              return sortDirection === SORTING_DIRECTIONS.ASC ? 1 : -1
            }
            return 0
          })
          break

        case SORTING_OPTIONS.SIZE:
          gcodes.sort(function(a, b) {
            if (sortDirection === SORTING_DIRECTIONS.ASC) {
              return a.num_bytes - b.num_bytes
            } else {
              return b.num_bytes - a.num_bytes
            }
          })
          break

        case SORTING_OPTIONS.CREATED:
          gcodes.sort(function(a, b) {
            const uploadedA = a.created_at.unix()
            const uploadedB = b.created_at.unix()
            if (sortDirection === SORTING_DIRECTIONS.ASC) {
              return uploadedA - uploadedB
            } else {
              return uploadedB - uploadedA
            }
          })
          break

        case SORTING_OPTIONS.LAST_PRINTED:
          gcodes.sort(function(a, b) {
            const printedA = a.last_printed_at?.unix() || 0
            const printedB = b.last_printed_at?.unix() || 0
            if (sortDirection === SORTING_DIRECTIONS.ASC) {
              return printedA - printedB
            } else {
              return printedB - printedA
            }
          })
          break
      }

      return gcodes
    },
    foldersToShow() {
      let folders = this.folders

      if (!folders) {
        return []
      }

      const sortDirection = this.activeSortingDirection

      switch (this.activeSorting) {
        case SORTING_OPTIONS.NAME:
          folders.sort(function(a, b) {
            var nameA = a.name.toUpperCase() // ignore upper and lowercase
            var nameB = b.name.toUpperCase() // ignore upper and lowercase
            if (nameA < nameB) {
              return sortDirection === SORTING_DIRECTIONS.ASC ? -1 : 1
            }
            if (nameA > nameB) {
              return sortDirection === SORTING_DIRECTIONS.ASC ? 1 : -1
            }
            return 0
          })
          break

        case SORTING_OPTIONS.SIZE:
          folders.sort(function(a, b) {
            if (sortDirection === SORTING_DIRECTIONS.ASC) {
              return a.numItems - b.numItems
            } else {
              return b.numItems - a.numItems
            }
          })
          break

        case SORTING_OPTIONS.CREATED:
          folders.sort(function(a, b) {
            const createdA = a.created_at.unix()
            const createdB = b.created_at.unix()
            if (sortDirection === SORTING_DIRECTIONS.ASC) {
              return createdA - createdB
            } else {
              return createdB - createdA
            }
          })
          break
      }
      return folders
    },
  },

  methods: {
    async fetchFilesAndFolders() {
      this.loading = true
      this.gcodes = []
      this.folders = []
      let files
      let folders

      try {
        files = await axios.get(
          urls.gcodeFiles({parentFolder: this.parentFolder}), {
            // If cache is enabled, after renaming item on gcode page
            // and going back to files - gcode will have old name
            headers: {'Cache-Control': 'no-cache'}
          })
        folders = await axios.get(
          urls.gcodeFolders({parentFolder: this.parentFolder}))
      } catch (e) {
        this.loading = false
        console.error(e)
      }

      files = files?.data
      folders = folders?.data
      if (files?.count) {
        this.gcodes = files.results.map(data => normalizedGcode(data))
      }
      if (folders?.count) {
        this.folders = folders.results.map(data => normalizedGcodeFolder(data))
      }
      this.loading = false
    },
    updateSearch(search) {
      clearTimeout(this.searchTimeoutId)
      this.searchTimeoutId = null

      this.searchStateIsActive = !!search
      if (!this.searchStateIsActive) {
        this.searchResultGcodes = []
        return
      }

      this.searchTimeoutId = setTimeout(async () => {
        this.loading = true
        this.searchResultGcodes = []
        let files

        try {
          files = await axios.get(urls.gcodeFiles({query: search}))
        } catch (e) {
          this.loading = false
          console.error(e)
        }

        files = files?.data
        if (files?.count) {
          this.searchResultGcodes = files.results.map(data => normalizedGcode(data))
        }

        this.loading = false
        this.searchTimeoutId = null
      }, SEARCH_API_CALL_DELAY);
    },
    updateSorting(sortOption) {
      if (this.activeSorting === sortOption) {
        this.activeSortingDirection = -this.activeSortingDirection
      } else {
        this.activeSorting = sortOption
        this.activeSortingDirection = SORTING_DIRECTIONS.ASC
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
      this.gcodes = []
      this.fetchFilesAndFolders()
    },
    gcodeUploadError(file, message) {
      this.$swal.Reject.fire({
        html: `<p class="text-center">${message}</p>`})
    },
    removeItem(id) {
      axios
        .delete(urls.gcode(id), )
        .then(() => {
          for (let i = 0; i < this.gcodes.length; i++) {
            const deleted = this.gcodes[i]

            if (deleted.id === id) {
              this.gcodes.splice(i, 1)

              // Toast for user
              let toastHtml = ''
              toastHtml += `<h6 class="text-danger">${deleted.filename} successfully deleted!</h6>`

              this.$swal.Toast.fire({
                // icon: 'success',
                html: toastHtml,
              })
            }
          }
        })
    },
    renameItem(id, oldName, itemType = 'file') {
      this.$swal.Prompt.fire({
        title: 'New name',
        input: 'text',
        inputValue: oldName,
        inputPlaceholder: 'New name',
        showCancelButton: true,
        confirmButtonText: 'Save',
        preConfirm: async (newName) => {
          if (!newName) {
            this.$swal.showValidationMessage('Name is required')
            return false
          }
          if (itemType === 'folder' && this.folders.find(item => item.name === newName)) {
            this.$swal.showValidationMessage('Folder with this name already exists')
            return false
          }
          try {
            const url = itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
            await axios.patch(url, `${itemType === 'file' ? 'filename' : 'name'}=${newName}`)
          } catch (e) {
            this.$swal.showValidationMessage('Server error')
            console.log(e)
            return false
          }
          this.fetchFilesAndFolders()
          return true
        },
      })
    },
    deleteItem(id, itemType = 'file') {
      this.$swal.Confirm.fire().then(async userAction => {
        if (userAction.isConfirmed) {
          try {
            const url = itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
            await axios.delete(url)
            this.fetchFilesAndFolders()
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
    createFolder() {
      this.$swal.fire({
        title: 'Create folder',
        input: 'text',
        inputLabel: 'Folder name',
        inputPlaceholder: 'Folder name',
        showCancelButton: true,
        confirmButtonText: 'Create',
        preConfirm: async (folderName) => {
          if (!folderName) {
            this.$swal.showValidationMessage('Folder name is required')
            return false;
          }
          if (this.folders.find(item => item.name === folderName)) {
            this.$swal.showValidationMessage('Folder with this name already exists')
            return false;
          }
          try {
            await axios.post(urls.gcodeFolders(), {
              name: folderName,
              parent_folder: this.parentFolder
            })
          } catch (e) {
            this.$swal.showValidationMessage('Server error')
            console.log(e);
            return false;
          }
          this.fetchFilesAndFolders();
          return true;
        },
      })
    },
    openFolder(folder) {
      // Prevent navigation if main user action was to click dropdown item
      if (document.querySelector('.swal2-container')) {
        return false
      }
      this.$router.push(`/g_code_folders/${folder.id}/`)
    },
    openFile(file) {
      // Prevent navigation if main user action was to click dropdown item
      if (document.querySelector('.swal2-container')) {
        return false
      }
      window.location.assign(`/g_code_files/${file.id}/`)
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

.sorting-panel
  display: flex
  padding: 1em calc(1em + 30px) 1em 1em
  border-bottom: 1px solid var(--color-divider)
  font-weight: bold

  .sorting-option
    flex: 1
    display: flex
    justify-content: space-between
    margin-left: 30px
    align-items: center
    font-size: .9rem

    &:hover
      cursor: pointer

    &:first-child
      margin-left: 0
      flex: 3

    .direction
      font-size: .8rem
      opacity: .3

  .sorting-option.active .direction
    opacity: 1

  @media (max-width: 768px)
    &
      display: none

    .remove-button-placeholder
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
