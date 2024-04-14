<template>
  <b-modal
    id="b-modal-move"
    :title="$t('Move item')"
    :ok-title="$t('Place Here')"
    :cancel-title="$t('Cancel')"
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
          :title="$t('Go Back')"
          @click.prevent="goBack"
        >
          <i class="fas fa-chevron-left"></i>
        </a>
        <h5 class="modal-title">{{ $t("Move item") }}</h5>
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
        :no-more-files="true"
        :is-move-modal="true"
        :disabled-items="disabledItems"
        @openFolder="openFolder"
        @fetchMore="fetchFilesAndFolders"
      />
    </form>
  </b-modal>
</template>

<script>
import urls from '@config/server-urls'
import axios from 'axios'
import GCodeFileStructure from '@src/components/g-codes/GCodeFileStructure.vue'
import { normalizedGcodeFolder } from '@src/lib/normalizers'

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
    items: {
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
    sortingValue: {
      type: Object,
      required: true,
    },
    itemParentFolderId: {
      type: String,
      default: '',
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
      currentFoldersPage: 1,
      currentFilesPage: 1,
    }
  },

  computed: {
    disabledItems() {
      const items = {
        files: [],
        folders: [],
      }

      if (this.item && this.itemType === 'file') {
        items.files = [this.item.id]
      } else if (this.item && this.itemType === 'folder') {
        items.folders = [this.item.id]
      } else if (this.items) {
        items.files = this.items.files
        items.folders = this.items.folders
      }

      return items
    },
    itemType() {
      return this.item ? (this.item.filename ? 'file' : 'folder') : null
    },
    parentFolder() {
      return this.path && this.path.length > 0 ? this.path.at(-1) : null
    },
    isSameDir() {
      if (this.parentFolder === null && !this.itemParentFolderId) {
        return true
      } else if (parseInt(this.itemParentFolderId) === this.parentFolder) {
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

      if (this.noMoreFolders) {
        return
      }

      this.loading = true
      let folders = []

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

        this.folders.push(...folders.map((data) => normalizedGcodeFolder(data)))
        this.currentFoldersPage += 1
      }

      this.loading = false
    },

    show() {
      this.isOpen = true
      this.fetchFilesAndFolders()

      this.$nextTick(() => {
        if (!this.item && !this.items) {
          this.isOpen = false
          return
        }
        this.$bvModal.show('b-modal-move')
      })
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
      this.patchLoading = true
      const parentFolder = this.parentFolder || ''

      try {
        if (this.item) {
          const id = this.item.id
          const url = this.itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
          await axios.patch(url, `parent_folder=${parentFolder}`)
        } else if (this.items) {
          if (this.items.folders.length)
            await axios.post(urls.gcodeFolderBulkMove(), {
              folder_ids: this.items.folders,
              parent_folder: parentFolder,
            })
          if (this.items.files.length)
            await axios.post(urls.gcodeFileBulkMove(), {
              file_ids: this.items.files,
              parent_folder: parentFolder,
            })
        }
      } catch (error) {
        this.errorDialog(error, `${this.$i18next.t('Failed to move item(s)')}`)
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
