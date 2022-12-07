<template>
  <layout>
    <template v-slot:topBarLeft>
      <search-input @input="updateSearch" class="search-input mr-3"></search-input>
    </template>
    <template v-slot:topBarRight>
      <div>
        <a href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Upload G-Code">
          <i class="fas fa-file-upload"></i>
        </a>
        <a @click.prevent="createFolder" href="#" class="btn shadow-none icon-btn d-none d-md-inline" title="Create folder">
          <i class="fas fa-folder-plus"></i>
        </a>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item href="#" class="d-md-none">
            <i class="fas fa-file-upload"></i>Upload G-Code
          </b-dropdown-item>
          <b-dropdown-item href="#" class="d-md-none">
            <i class="fas fa-folder-plus"></i>Create Folder
          </b-dropdown-item>
          <b-dropdown-divider class="d-md-none"></b-dropdown-divider>
          <b-dropdown-text class="small">ORDER</b-dropdown-text>
          <b-dropdown-item v-for="sortingOption in sortingOptions" :key="`s_${sortingOption}`">
            <div @click="() => activeSorting = sortingOption" class="clickable-area">
              <i class="fas fa-check text-primary" :style="{visibility: activeSorting === sortingOption ? 'visible' : 'hidden'}"></i>
              {{ sortingTitle[sortingOption] }}
            </div>
          </b-dropdown-item>
          <b-dropdown-divider />
          <b-dropdown-item v-for="sortingDirection in sortingDirections" :key="`d_${sortingDirection}`">
            <div @click="() => activeSortingDirection = sortingDirection" class="clickable-area">
              <i class="fas fa-check text-primary" :style="{visibility: activeSortingDirection === sortingDirection ? 'visible' : 'hidden'}"></i>
              {{ sortingDirectionTitle[sortingDirection] }}
            </div>
          </b-dropdown-item>
        </b-dropdown>
      </div>
    </template>
    <template v-slot:content>
      <b-container>
        <b-row>
          <b-col>
            <!-- <vue-dropzone
              class="upload-box"
              id="dropzone"
              :options="dropzoneOptions"
              :useCustomSlot="true"
              @vdropzone-queue-complete="gcodeUploadSuccess"
              @vdropzone-error="gcodeUploadError"
              ref="gcodesDropzone"
            >
              <div class="dz-message needsclick">
                <i class="fas fa-upload fa-2x"></i> <br>
                <div>G-Code file (*.gcode, *.gco, or *.g) only.</div>
                <div>Up to {{maxFilesize}} MB each file, {{maxTotalFilesize}} GB total.</div>
              </div>
            </vue-dropzone> -->

            <!-- GCodes list -->
            <div class="gcodes-wrapper">
              <div class="control-panel">
                <!-- <search-input v-model="searchText" class="search-input"></search-input> -->
              </div>

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
                <div v-for="item in folders" :key="`folder_${item.id}`" class="item">
                  <div class="item-info">
                    <div class="filename">
                      <i class="fas fa-folder mr-1"></i>
                      {{ item.name }}
                    </div>
                    <div class="filesize">{{ item.numItems }} item(s)</div>
                    <div class="uploaded">{{ item.created_at.fromNow() }}</div>
                    <div class="last-printed"></div>
                  </div>
                  <div>
                    <b-dropdown right no-caret toggle-class="icon-btn">
                      <template #button-content>
                        <i class="fas fa-ellipsis-v"></i>
                      </template>
                      <b-dropdown-item>
                        <i class="fas fa-edit"></i>Rename
                      </b-dropdown-item>
                      <b-dropdown-item>
                        <i class="fas fa-arrows-alt"></i>Move
                      </b-dropdown-item>
                      <b-dropdown-item>
                        <div @click="deleteItem(item.id, 'folder')" class="clickable-area">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </div>
                      </b-dropdown-item>
                    </b-dropdown>
                  </div>
                </div>

                <div v-for="item in gcodesToShow" :key="`gcode_${item.id}`" class="item">
                  <div class="item-info">
                    <div class="filename">
                      <i class="fas fa-file-code mr-1"></i>
                      {{ item.filename }}
                    </div>
                    <div class="filesize">{{ item.filesize }}</div>
                    <div class="uploaded">{{ item.created_at.fromNow() }}</div>
                    <div class="last-printed">{{ item.created_at.fromNow() }}</div>
                  </div>
                  <div>
                    <b-dropdown right no-caret toggle-class="icon-btn">
                      <template #button-content>
                        <i class="fas fa-ellipsis-v"></i>
                      </template>
                      <b-dropdown-item>
                        <span class="text-primary">
                          <i class="fas fa-play-circle"></i>Print
                        </span>
                      </b-dropdown-item>
                      <b-dropdown-item>
                        <i class="fas fa-edit"></i>Rename
                      </b-dropdown-item>
                      <b-dropdown-item>
                        <i class="fas fa-arrows-alt"></i>Move
                      </b-dropdown-item>
                      <b-dropdown-item>
                        <div @click="deleteItem(item.id, 'file')" class="clickable-area">
                          <span class="text-danger">
                            <i class="fas fa-trash-alt"></i>Delete
                          </span>
                        </div>
                      </b-dropdown-item>
                    </b-dropdown>
                  </div>
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
      searchText: '',
      activeSorting: SORTING_OPTIONS.CREATED,
      activeSortingDirection: SORTING_DIRECTIONS.DESC,
      sortingOptions: SORTING_OPTIONS,
      sortingTitle: SORTING_OPTIONS_TITLE,
      sortingDirectionTitle: SORTING_DIRECTION_TITLE,
      sortingDirections: SORTING_DIRECTIONS,
      gcodes: [],
      folders: [],
      currentPage: 1,
      loading: false,
    }
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
        url: 'upload/',
        headers: { 'X-CSRFToken': this.csrf },
      }
    },

    gcodesToShow() {
      let gcodes = this.gcodes

      if (!gcodes) {
        return []
      }

      const query = this.searchText.toLowerCase()
      gcodes = gcodes.filter((gcf) => gcf.filename.toLowerCase().indexOf(query) > -1)

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
      }

      return gcodes
    },
  },

  created() {
    this.user = user()
    this.fetchGCodes()
    // this.createGcodeFolder()
  },

  methods: {
    createFolder() {
      this.$swal.fire({
        title: 'Create folder',
        input: 'text',
        inputLabel: 'Folder name',
        inputPlaceholder: 'Folder name',
        showCancelButton: true,
        confirmButtonText: 'Create',
        backdrop: 'rgba(0,0,0,0.5)',
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
              parent_folder: null,
            })
          } catch (e) {
            this.$swal.showValidationMessage('Server error')
            console.log(e);
            return false;
          }
          this.fetchGCodes();
          return true;
        },
      })
    },
    deleteItem(id, type = 'file') {
      this.$swal.Prompt.fire({
        title: 'Are you sure?',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
      }).then(async userAction => {
        if (userAction.isConfirmed) {
          try {
            const url = type === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
            await axios.delete(url)
            this.fetchGCodes()
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
    updateSearch(search) {
      this.searchText = search
    },
    gcodeUploadSuccess() {
      this.$refs.gcodesDropzone.removeAllFiles()

      this.gcodes = []
      this.currentPage = 1
      this.fetchGCodes()
    },

    gcodeUploadError(file, message) {
      this.$swal.Reject.fire({
        html: `<p class="text-center">${message}</p>`})
    },

    async createGcodeFolder() {
      await axios.post('/api/v1/g_code_folders/', {
        name: 'test name',
        parent_folder: null,
      })
    },

    async fetchGCodes() {
      this.loading = true

      this.gcodes = []
      this.folders = []

      let files
      let folders

      try {
        files = await axios.get(urls.gcodeFiles())
        folders = await axios.get(urls.gcodeFolders())
      } catch (e) {
        this.loading = false
        console.error(e)
      }

      files = files?.data
      folders = folders?.data

      // console.log(folders)

      if (files?.count) {
        this.gcodes = files.results.map(data => normalizedGcode(data))
      }

      if (folders?.count) {
        folders = folders.results.map(data => normalizedGcodeFolder(data))

        for (let folder in folders) {
          try {
            const numFiles = (await axios.get(urls.gcodeFiles({parentFolder: folders[folder].id}))).data.count || 0
            const numFolders = (await axios.get(urls.gcodeFolders({parentFolder: folders[folder].id}))).data.count || 0
            folders[folder].numItems = numFiles + numFolders
          } catch (e) {
            this.loading = false
            console.error(e)
          }
        }

        this.folders = folders
      }

      this.loading = false
    },

    // fetchGCodeFolders() {
    //   this.loading = true

    //   return axios
    //     .get(urls.gcodeFiles(this.currentPage))
    //     .then(response => {
    //       this.loading = false

    //       let gcodeFiles = response.data.results

    //       if (gcodeFiles) {
    //         this.gcodes.push(...gcodeFiles.map(data => normalizedGcode(data)))
    //         this.currentPage += 1
    //       }
    //     }).catch(err => {
    //       console.log(err)
    //     })
    // },

    updateSorting(sortOption) {
      if (this.activeSorting === sortOption) {
        this.activeSortingDirection = -this.activeSortingDirection
      } else {
        this.activeSorting = sortOption
        this.activeSortingDirection = SORTING_DIRECTIONS.ASC
      }
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
    }
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
  padding: 2em
  border-radius: var(--border-radius-lg)
  min-height: 70vh

.control-panel
  border-bottom: 1px solid var(--color-divider)
  padding-bottom: 16px

.sorting-panel
  display: flex
  padding: 1em calc(1em + 30px) 1em 1em
  border-bottom: 1px solid var(--color-divider)

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

    .direction
      font-size: .8rem
      opacity: .3

  .sorting-option.active .direction
    opacity: 1

  @media (max-width: 768px)
    &
      flex-direction: column
      padding: 1em 0

    .sorting-option
      margin-left: 0
      margin-bottom: 4px

    .remove-button-placeholder
      display: none

.gcode-items-wrapper
  .item
    display: flex
    align-items: center
    padding: .6em 1em

    &:nth-child(2n)
      background-color: var(--color-table-accent)

    .item-info
      display: flex
      width: 100%
      overflow: hidden
      flex: 1

      div
        flex: 1
        margin-left: 30px

        &:first-child
          margin-left: 0

      .filename
        text-overflow: ellipsis
        overflow: hidden
        white-space: nowrap
        width: 100%

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
        padding: .6em 0

      &:nth-child(2n)
        margin: 0 -.6em
        padding: .6em

      .item-info
        flex-direction: column
        align-items: flex-start

        div
          margin-left: 0
</style>
