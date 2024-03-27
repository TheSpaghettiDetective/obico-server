<template>
  <div class="printer-event-card my-3" :class="tintBorderClass">
    <div class="printer-event-text" :class="{ link: printerEvent.info_url }" @click="onTextClick">
      <div class="title font-weight-bold my-2" :class="tintClass">
        {{ eventTitle }}
        <i v-if="printerEvent.info_url" class="fas fa-external-link-alt"></i>
      </div>
      <div class="description" v-html="printerEvent.event_text"></div>
      <div class="my-2 text-muted font-weight-light small">
        {{ printerEvent.created_at.format('LLLL') }}
      </div>
    </div>
    <div
      v-if="printerEvent.image_url"
      :style="{ backgroundImage: `url(${printerEvent.image_url})` }"
      class="printer-event-snapshot"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'PrinterEventCard',

  components: {},

  props: {
    printerEvent: {
      type: Object,
      required: true,
    },
  },

  computed: {
    eventTitle() {
      return this.printerEvent.event_title || `${this.$i18next.t('Unknown event')}`
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
        window.open(this.printerEvent.info_url, '_blank')
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-event-card
  display: flex
  justify-content: space-between
  border-radius: var(--border-radius-sm)
  background-color: var(--color-surface-secondary)
  border-left: solid thick

  >:last-child
    border-top-right-radius: inherit
    border-bottom-right-radius: inherit

.printer-event-text
  flex: 1
  padding: 0px 14px
  overflow: hidden

  .title
    display: flex
    justify-content: space-between

  &.link
    &:hover
      cursor: pointer
      opacity: .9

  .description ::v-deep div
    text-overflow: ellipsis
    overflow: hidden
    white-space: nowrap

.printer-event-snapshot
  flex: 0 0 120px
  background-size: cover
  background-repeat: no-repeat
  background-position: center center
</style>
