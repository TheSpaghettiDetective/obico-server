<template>
  <b-modal
    id="b-modal-rename"
    :title="$t('Enter new name')"
    :ok-title="$t('Rename')"
    :cancel-title="$t('Cancel')"
    centered
    @ok="handleOk"
    @hidden="resetModal"
    @shown="focusInput"
  >
    <form @submit.prevent="handleSubmit">
      <div class="my-2">
        <input
          ref="input"
          v-model="newItemName"
          type="text"
          name="name"
          :placeholder="$t('New name')"
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
  name: 'RenameModal',

  components: {},

  props: {
    item: {
      type: Object,
      default: null,
    },
    preConfirm: {
      type: Function,
      default: null,
    },
  },

  data() {
    return {
      newItemName: '',
      errorMessage: '',
      isOpen: false,
    }
  },

  computed: {
    itemType() {
      return this.item.filename ? 'file' : 'folder'
    },
    fullName() {
      if (this.itemType === 'file') {
        return `${this.newItemName}.${this.fileExt}`
      } else {
        return this.newItemName
      }
    },
    fileExt() {
      if (this.itemType === 'folder') return null
      return this.item.filename.split('.').at(-1)
    },
    nameWithoutExt() {
      if (this.itemType === 'folder') {
        return this.item.name
      } else {
        const filename = this.item.filename
        return filename.slice(0, filename.length - this.fileExt.length - 1)
      }
    },
    newNameWithExt() {
      if (this.itemType === 'folder') {
        return this.newItemName
      } else {
        return `${this.newItemName}.${this.fileExt}`
      }
    },
  },

  methods: {
    show() {
      this.isOpen = true

      this.$nextTick(() => {
        if (!this.item) {
          this.isOpen = false
          return
        }
        this.newItemName = this.nameWithoutExt
        this.$bvModal.show('b-modal-rename')
      })
    },
    focusInput() {
      this.$refs.input.select()
    },
    close() {
      this.$bvModal.hide('b-modal-rename')
      this.resetModal()
    },
    resetModal() {
      this.isOpen = false
      this.newItemName = ''
      this.errorMessage = ''
    },
    handleOk(bvModalEvent) {
      if (this.newNameWithExt === (this.item.filename || this.item.name)) {
        this.close()
        return
      }

      bvModalEvent.preventDefault()
      this.handleSubmit()
    },
    async handleSubmit() {
      const id = this.item.id

      if (!this.newItemName) {
        return
      }

      if (this.newNameWithExt === (this.item.filename || this.item.name)) {
        this.close()
        return
      }

      if (this.preConfirm) {
        const result = this.preConfirm(this.newNameWithExt)
        if (result !== true) {
          this.errorMessage = result
          return
        }
      }

      try {
        const url = this.itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
        await axios.patch(
          url,
          `${this.itemType === 'file' ? 'filename' : 'name'}=${this.newNameWithExt}`
        )
      } catch (e) {
        this.errorMessage = `${this.$i18next.t('Server error')}`
        console.log(e)
        return
      }

      this.$emit('renamed', this.newNameWithExt)
      this.close()
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
