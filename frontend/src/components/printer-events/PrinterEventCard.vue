<template>
  <div class="printer-event-card my-3" :class="tintBorderClass">
    <div class="d-flex pl-2">
      <div class="printer-event-text" :class="{link: printerEvent.info_url}" @click="onTextClick">
        <div class="title font-weight-bold my-2" :class="tintClass">
          {{ eventTitle }}
          <i v-if="printerEvent.info_url" class="fas fa-external-link-alt"></i>
        </div>
        <div class="my-2 text-muted" v-html="printerEvent.event_text"></div>
      </div>
      <div v-if="printerEvent.image_url" class="printer-event-snapshot">
        <img :src="printerEvent.image_url" />
      </div>
    </div>
    <div class="printer-event-footer d-flex w-100 justify-content-between align-items-center pl-2">
      <div class="font-weight-light small">
        {{ printerEvent.created_at.format('LLLL') }}
      </div>
      <button class="btn" type="button" @click="suppressPrinterEvent">
        <i class="fas fa-bell-slash"></i>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrinterEventCard',

  components: {
  },

  props: {
    printerEvent: Object
  },

  computed: {
    eventTitle() {
      return this.printerEvent.event_title || 'Unknown event'
    },
    tintClass() {
      switch (this.printerEvent.event_class) {
        case 'ERROR':
          return 'text-danger'
        case 'WARNING':
          return 'text-warning'
        case 'SUCCESS':
          return 'text-success'
        default:
          return ''
      }
    },
    tintBorderClass() {
      switch (this.printerEvent.event_class) {
        case 'ERROR':
          return 'border-danger'
        case 'WARNING':
          return 'border-warning'
        case 'SUCCESS':
          return 'border-success'
        default:
          return ''
      }
    },
  },

  methods: {
    onTextClick() {
      if (this.printerEvent.info_url) {
        window.open(this.printerEvent.info_url, '_blank');
      }
    },
    suppressPrinterEvent() {
      this.$swal.Prompt.fire({
        title: 'Test',
        html: `
          Are you sure?
        `,
        showCloseButton: true,
      })
    },
  }
}
</script>

<style lang="sass" scoped>
.printer-event-card
  justify-content: space-between
  align-items: start
  border-radius: var(--border-radius-sm)
  display: flex
  flex-direction: column
  background-color: var(--color-surface-primary)
  border-left: solid thick

  >:first-child
    border-top-right-radius: inherit
  >:last-child
    border-bottom-right-radius: inherit

.printer-event-text
  flex: 1

  .title
    display: flex
    justify-content: space-between

  &.link
    &:hover
      cursor: pointer
      opacity: .9

.printer-event-snapshot
  max-width: 25%
  border-top-right-radius: inherit

  img
    object-fit: contain
    width: 100%
    border-radius: inherit

.printer-event-footer
  background-color: var(--color-surface-secondary)
</style>
