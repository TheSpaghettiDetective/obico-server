<template>
  <div class="print-container" @click="openPrint">
    <div class="status-indicator" :class="print.status.key"></div>
    <div class="main-content overflow-truncated-parent">
      <div class="top">
        <div class="title overflow-truncated">{{ print.filename }}</div>
      </div>
      <div class="bottom">
        <div class="info">
          <svg width="1em" height="1em" class="icon">
            <use href="#svg-3d-printer" />
          </svg>
          <span>{{ print.printer ? print.printer.name : 'Unavailable' }}</span>
        </div>
        <div class="info">
          <i class="far fa-clock icon"></i>
          <span v-if="print.ended_at">{{ print.ended_at.fromNow() }}</span>
          <span v-else>Printing...</span>
        </div>
        <div v-if="print.need_alert_overwrite" class="info feedback-info">
          <span>Review Needed</span>
        </div>
        <div v-if="print.need_print_shot_feedback" class="info feedback-info focused">
          <span>Focused-Review Needed</span>
        </div>
      </div>
    </div>
    <div v-if="print.poster_url" class="poster">
      <div class="img" :style="{ backgroundImage: `url(${print.poster_url})` }"></div>
    </div>
  </div>
</template>

<script>
import { PrintStatus } from '@src/lib/normalizers'

export default {
  name: 'PrintHistoryItem',

  components: {},

  props: {
    print: {
      type: Object,
      required: true,
    },
  },

  data: function () {
    return {
      PrintStatus,
    }
  },

  methods: {
    openPrint() {
      window.location.assign(`/prints/${this.print.id}/`)
    },
  },
}
</script>

<style lang="sass" scoped>
.print-container
  display: flex
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)
  overflow: hidden
  &:hover
    cursor: pointer
    background: var(--color-hover-accent)
    transition: all .3s ease-out

.status-indicator
  flex: 0 0 5px
  &.finished
    background-color: var(--color-success)
  &.cancelled
    background-color: var(--color-danger)
  &.printing
    background-color: var(--color-text-primary)

.main-content
  padding: 1rem
  flex: 1

.top
  display: flex
  align-items: flex-end
  margin-bottom: .25rem

.title
  font-weight: bold

.bottom
  display: flex
  align-items: center
  justify-content: flex-start
  gap: 14px
  @media (max-width: 768px)
    flex-direction: column
    gap: 2px
    align-items: flex-start

.info
  display: flex
  gap: .25em
  align-items: center
  font-size: 0.9375rem
  overflow: hidden
  max-width: 50%

  span
    text-overflow: ellipsis
    white-space: nowrap
    overflow: hidden

  @media (max-width: 768px)
    max-width: 100%

.icon
  color: var(--color-text-secondary)
  font-size: .8em
  flex-shrink: 0

  &.fa-clock
    position: relative
    top: 1px

.feedback-info
  background-color: var(--color-surface-primary)
  padding: .0625em .625em
  border-radius: var(--border-radius-xs)
  font-size: 0.8125rem
  margin: 2px 0
  &.focused
    background-color: var(--color-primary)
    color: var(--color-on-primary)

.poster
  margin-left: auto
  .img
    background-size: cover
    background-position: center
    height: 100%
    width: 100px
    background-color: var(--color-hover)
    display: flex
    justify-content: center
    align-items: center
    color: var(--color-text-secondary)
    font-size: 0.875rem
</style>
