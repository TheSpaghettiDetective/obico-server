<template>
  <div></div>
</template>

<script>
import urls from '@config/server-urls'
import axios from 'axios'

export default {
  name: 'RenameModal',

  props: {
    item: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      isOpen: false,
    }
  },

  created() {},

  mounted() {},

  methods: {
    show() {
      this.isOpen = true
      this.$bvModal
        .msgBoxConfirm(`${this.$i18next.t('Are you sure?')}`, {
          id: 'b-modal-confirm-delete',
          centered: true,
          okTitle: `${this.$i18next.t('Delete')}`,
          okVariant: 'danger',
          size: 'sm',
          autoFocusButton: 'ok',
        })
        .then(async (value) => {
          this.isOpen = false
          if (!value) return

          try {
            const url = this.item.filename
              ? urls.gcodeFile(this.item.id)
              : urls.gcodeFolder(this.item.id)
            await axios.delete(url)
          } catch (e) {
            console.log(e)
            return
          }

          this.$emit('deleted')
        })
        .catch((error) => {
          this.errorDialog(error, `${this.$i18next.t('Failed to delete item')}`)
        })
    },
  },
}
</script>

<style lang="sass">
#b-modal-confirm-delete
  .modal-body
    font-size: 1.125rem
    text-align: center
  .modal-footer
    justify-content: center
</style>
