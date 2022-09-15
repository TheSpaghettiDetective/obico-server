<template>
  <div class="printer-event-card">
    <div class="printer-event-class-hint" :class="tintClass">
    </div>
    <div class="printer-event-text" :class="{link: printerEvent.help_url}" v-on:click="onTextClick">
      <div class="title font-weight-bold my-2" :class="tintClass">
        {{ eventTitle }}
        <i v-if="printerEvent.help_url" class="fas fa-external-link-alt"></i>
      </div>
      <div>
        {{ printerEvent.event_text }}
      </div>
      <div class="my-2 text-muted font-weight-light small">
        {{ printerEvent.created_at.format('LLLL') }}
      </div>
    </div>
    <div v-if="printerEvent.image_url" class="printer-event-snapshot">
      <img :src="printerEvent.image_url" />
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
  },

  methods: {
    onTextClick() {
      if (this.printerEvent.help_url) {
        window.open(this.printerEvent.help_url, '_blank');
      }
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
  background-color: var(--color-surface-secondary)

  >:last-child
    border-top-right-radius: inherit
    border-bottom-right-radius: inherit

.printer-event-class-hint
  border-style: solid
  border-width: 3px
  position: absolute
  bottom: 0
  top: 0
  border-top-left-radius: inherit
  border-bottom-left-radius: inherit

.printer-event-text
  padding: 0px 14px

  .title
    display: flex
    justify-content: space-between

  &.link
    &:hover
      cursor: pointer
      opacity: .9

.printer-event-snapshot
  max-width: 25%

  img
    object-fit: contain
    width: 100%
    border-radius: inherit
</style>
