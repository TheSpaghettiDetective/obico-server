<template>
  <b-modal
    id="b-modal-rename"
    title="Enter new name"
    ok-title="Rename"
    centered
    @ok="handleOk"
    @hidden="resetModal"
    @shown="focusInput"
  >
    <form @submit.prevent="handleSubmit">
      <div class="my-2">
        <input
          ref="input"
          type="text"
          name="name"
          placeholder="New name"
          class="input-lg"
          required="required"
          v-model="newItemName"
        >
        <b-alert v-if="errorMessage" variant="danger" class="mt-3" show>
          {{ errorMessage }}
        </b-alert>
      </div>
    </form>
  </b-modal>
</template>

<script>
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
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
      itemType: '',
      errorMessage: '',
      isOpen: false,
    }
  },

  methods: {
    show() {
      this.isOpen = true

      setTimeout(() => {
        if (!this.item) {
          this.isOpen = false
          return
        }
        this.newItemName = this.item.filename || this.item.name
        this.itemType = this.item.filename ? 'file' : 'folder'
        this.$bvModal.show('b-modal-rename')
      }, 100)
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
      this.itemType = ''
      this.errorMessage = ''
    },
    handleOk(bvModalEvent) {
      bvModalEvent.preventDefault()
      this.handleSubmit()
    },
    async handleSubmit() {
      const itemType = this.itemType
      const id = this.item.id

      if (!this.newItemName) {
        return
      }

      if (this.newItemName === (this.item.filename || this.item.name)) {
        this.$bvModal.hide('b-modal-rename')
        return
      }

      if (this.preConfirm) {
        const result = this.preConfirm(this.newItemName)
        if (result !== true) {
          this.errorMessage = result
          return
        }
      }

      try {
        const url = itemType === 'file' ? urls.gcodeFile(id) : urls.gcodeFolder(id)
        await axios.patch(url, `${itemType === 'file' ? 'filename' : 'name'}=${this.newItemName}`)
      } catch (e) {
        this.errorMessage = 'Server error'
        console.log(e)
        return
      }

      this.$emit('renamed', this.newItemName)
      this.$bvModal.hide('b-modal-rename')
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
