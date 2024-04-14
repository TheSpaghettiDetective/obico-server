<template>
  <b-modal
    id="b-modal-new-folder"
    :title="$t('Enter new folder name')"
    :ok-title="$t('Create')"
    :cancel-title="$t('Cancel')"
    :ok-disabled="!newFolderName.length"
    centered
    @ok="handleOk"
    @hidden="resetModal"
    @shown="focusInput"
  >
    <form @submit.prevent="handleSubmit">
      <div class="my-2">
        <input
          ref="input"
          v-model="newFolderName"
          type="text"
          name="name"
          :placeholder="$t('Folder name')"
          class="input-lg"
          required="required"
        />
        <b-alert v-if="errorMessage" variant="danger" class="mt-3" show>
          {{ errorMessage }}
        </b-alert>
      </div>
    </form>
  </b-modal>
</template>

<script>
import urls from '@config/server-urls'
import axios from 'axios'

export default {
  name: 'NewFolderModal',

  props: {
    preConfirm: {
      type: Function,
      default: null,
    },
    parentFolderId: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      newFolderName: '',
      errorMessage: '',
      isOpen: false,
    }
  },

  methods: {
    show() {
      this.isOpen = true
      this.$bvModal.show('b-modal-new-folder')
    },
    focusInput() {
      this.$refs.input.select()
    },
    resetModal() {
      this.isOpen = false
      this.newFolderName = ''
      this.errorMessage = ''
    },
    handleOk(bvModalEvent) {
      bvModalEvent.preventDefault()
      this.handleSubmit()
    },
    async handleSubmit() {
      if (!this.newFolderName) {
        return
      }

      if (this.preConfirm) {
        const result = this.preConfirm(this.newFolderName)
        if (result !== true) {
          this.errorMessage = result
          return
        }
      }

      try {
        const newFolder = await axios.post(urls.gcodeFolders(), {
          name: this.newFolderName,
          parent_folder: this.parentFolderId,
        })

        this.$emit('created', newFolder.data.id)
        this.$bvModal.hide('b-modal-new-folder')
      } catch (e) {
        console.log(e)
        return
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.input-lg
  height: 3rem
  padding: .5rem 1rem
  width: 100%
</style>
