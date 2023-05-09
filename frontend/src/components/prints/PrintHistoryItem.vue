<template>
  <a
    :href="`/prints/${print.id}/${index !== null ? '?index=' + index : ''}`"
    class="print-container"
  >
    <div class="status-indicator print-status-bg" :class="print.status.key"></div>
    <div v-if="selectable" class="checkbox-wrapper" :class="{ isSelected }">
      <b-form-checkbox v-model="isSelected" size="md"></b-form-checkbox>
    </div>
    <div class="main-content truncated-wrapper">
      <div class="top">
        <div class="title truncated" :title="fileName">{{ fileName }}</div>
      </div>
      <div class="bottom">
        <div class="info">
          <svg width="1em" height="1em" class="icon">
            <use href="#svg-3d-printer" />
          </svg>
          <span>{{ print.printer ? print.printer.name : 'Unavailable' }}</span>
        </div>
        <div class="info">
          <i class="fas fa-calendar-alt icon"></i>
          <span>{{ print.started_at.format('MMM D, YYYY') }}</span>
        </div>
      </div>
    </div>
    <div v-if="print.poster_url" class="poster">
      <div class="img" :style="{ backgroundImage: `url(${print.poster_url})` }"></div>
    </div>
    <div v-else class="poster no-photo">
      <svg>
        <use href="#svg-no-photo" />
      </svg>
    </div>
  </a>
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
    index: {
      type: Number,
      default: null,
    },
    selectable: {
      type: Boolean,
      default: false,
    },
    selected: {
      type: Boolean,
      default: false,
    },
  },

  data: function () {
    return {
      PrintStatus,
      isSelected: this.selected,
    }
  },

  computed: {
    fileName() {
      return this.print.g_code_file === null ? this.print.filename : this.print.g_code_file.filename
    },
  },

  watch: {
    isSelected(newValue) {
      this.$emit('selectedChanged', this.print.id, newValue)
    },
    selected(newValue) {
      this.isSelected = newValue
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
  color: var(--color-text-primary)
  &:hover
    cursor: pointer
    background: var(--color-hover-accent)
    transition: all .3s ease-out

.status-indicator
  flex: 0 0 5px
  margin-right: 1rem

.checkbox-wrapper
  display: flex
  align-items: flex-start
  justify-content: flex-end
  padding-top: 1rem
  ::v-deep .custom-checkbox .custom-control-label::before
    border-radius: var(--border-radius-xs)
    border-color: var(--color-divider)
  &.isSelected
    ::v-deep .custom-checkbox .custom-control-label::before
      border-color: #00C4B4

.main-content
  padding: 1rem
  padding-left: 0
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
  background-color: var(--color-hover)
  .img
    background-size: cover
    background-position: center
    height: 100%
    width: 100px
    display: flex
    justify-content: center
    align-items: center
    color: var(--color-text-secondary)
    font-size: 0.875rem
  &.no-photo
    width: 100px
    display: flex
    align-items: center
    justify-content: center
    svg
      width: 3rem
      height: 3rem
      color: var(--color-background)
</style>
