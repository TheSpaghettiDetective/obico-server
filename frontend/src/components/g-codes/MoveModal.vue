<template>
  <b-modal
    id="b-modal-move"
    title="Move item"
    ok-title="Place here"
    :ok-disabled="isSameDir || patchLoading"
    scrollable
    @ok="handleOk"
    @hidden="resetModal"
  >
    <template #modal-title>
      <div class="title">
        <a
          v-if="parentFolder !== null"
          href="#"
          class="btn shadow-none icon-btn d-inline"
          title="Go Back"
          @click.prevent="goBack"
        >
          <i class="fas fa-chevron-left"></i>
        </a>
        <h5 class="modal-title">Move item</h5>
      </div>
    </template>
    <form @submit.prevent="handleSubmit">
      <g-code-file-structure
        :folders="folders"
        :files="files"
        :target-printer="targetPrinter"
        :loading="loading"
        scroll-container-id="b-modal-move___BV_modal_body_"
        :no-more-folders="noMoreFolders"
        :no-more-files="noMoreFiles"
        :is-move-modal="true"
        :disabled-item="item"
        @openFolder="openFolder"
        @fetchMore="fetchFilesAndFolders"
      />
    </form>
  </b-modal>
</template>

<script>
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import urls from '@config/server-urls'
import axios from 'axios'
import GCodeFileStructure from '@src/components/g-codes/GCodeFileStructure.vue'
import { normalizedGcode, normalizedGcodeFolder } from '@src/lib/normalizers'

const PAGE_SIZE = 24

export default {
  name: 'MoveModal',

  components: {
    GCodeFileStructure,
  },

  props: {
    item: {
      type: Object,
      default: null,
    },
    targetPrinter: {
      type: Object,
      default: null,
    },
    scrollContainerId: {
      type: String,
      default: null,
    },
    activeSorting: {
      type: Object,
      required: true,
    },
    activeSortingDirection: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      path: [],
      isOpen: false,
      loading: false,
      patchLoading: false,
      folders: [],
      files: [],
      noMoreFolders: false,
      noMoreFiles: false,
      currentFoldersPage: 1,
      currentFilesPage: 1,
    }
  },

  computed: {
    itemType() {
      return this.item.filename ? 'file' : 'folder'
    },
    parentFolder() {
      return this.path && this.path.length > 0 ? this.path.at(-1) : null
    },
    isSameDir() {
      if (this.parentFolder === null && !this.item?.parent_folder) {
        return true
      } else if (this.item?.parent_folder && this.item?.parent_folder.id === this.parentFolder) {
        return true
      }
      return false
    },
  },

  methods: {
    goBack() {
      this.path.pop()
      this.fetchFilesAndFolders(true)
    },
    openFolder(folder) {
      this.path.push(folder.id)
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
    async fetchFilesAndFolders(reset = false) {
      if (this.loading) {
        return
      }

      if (reset) {
        this.resetFiles()
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
            params: {
              parent_folder: this.parentFolder || 'null',
              page: this.currentFilesPage,
              page_size: PAGE_SIZE,
              sorting: `${this.activeSorting.file_query}_${this.activeSortingDirection.query}`,
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

    show() {
      this.isOpen = true
      this.fetchFilesAndFolders()

      setTimeout(() => {
        if (!this.item) {
          this.isOpen = false
          return
        }
        this.$bvModal.show('b-modal-move')
      }, 100)
    },
    close() {
      this.$bvModal.hide('b-modal-move')
      this.resetModal()
    },
    resetModal() {
      this.isOpen = false
      this.path = []
      this.resetFiles()
    },
    handleOk(bvModalEvent) {
      bvModalEvent.preventDefault()
      this.handleSubmit()
    },
    async handleSubmit() {
      const id = this.item.id

      this.patchLoading = true

      try {
        const url = this.itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
        await axios.patch(url, `parent_folder=${this.parentFolder || ''}`)
      } catch (error) {
        this._showErrorPopup(error)
      }

      this.patchLoading = false
      this.$emit('moved')
      this.close()
    },
  },
}
</script>

<style lang="sass" scoped>
.title
  display: flex
  align-items: center
  .icon-btn
    padding-top: 0
    padding-bottom: 0
    padding-left: 0
</style>
