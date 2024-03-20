<template>
  <div
    class="item"
    :class="{ disabled: isDisabled, 'move-modal': isMoveModal }"
    @click="() => !isDisabled && $emit('click')"
  >
    <div v-if="selectable" class="checkbox-wrapper" :class="{ isSelected }">
      <b-form-checkbox
        size="md"
        :checked="isSelected"
        @click.native.capture.stop.prevent="isSelected = !isSelected"
      ></b-form-checkbox>
    </div>
    <div class="item-info">
      <div class="filename">
        <div class="thumbnail-wrapper" :class="{ folder: isFolder }">
          <div v-if="!isFolder && item.getSmallThumbnailUrl()" class="thumbnail">
            <img :src="item.getSmallThumbnailUrl()" />
          </div>
          <div v-else class="placeholder">
            <i v-if="isFolder" class="fas fa-folder"></i>
            <i v-else class="fas fa-file-code"></i>
          </div>
        </div>
        <span class="truncated">{{ isFolder ? item.name : item.filename }}</span>
      </div>

      <div class="size">
        <span v-if="!isFolder">{{ item.filesize }}</span>
        <span v-if="isFolder">{{ item.numItems }} item(s)</span>
      </div>
      <div v-if="!isMoveModal" class="created">
        {{ item.created_at ? item.created_at.fromNow() : '-' }}
      </div>
      <template v-if="!isMoveModal">
        <div v-if="!isFolder && isCloud" class="last-printed">
          <span v-if="!item.print_set">-</span>
          <span v-else-if="!item.print_set.length">{{$t('No prints yet')}}</span>
          <span v-else-if="item.last_print">{{
            item.last_print.ended_at ? item.last_print.ended_at.fromNow() : $t('Printing...')
          }}</span>
          <div
            v-if="item.last_print && item.last_print.ended_at"
            class="circle-indicator"
            :class="{
              cancelled: item.last_print.cancelled_at,
              finished: item.last_print.finished_at,
            }"
          ></div>
        </div>
        <div v-if="isFolder && isCloud" class="d-none d-md-block"></div>
      </template>
    </div>
    <div
      v-if="!isMoveModal && ((!isFolder && (isCloud || targetPrinter)) || (isFolder && isCloud))"
    >
      <b-dropdown right no-caret toggle-class="icon-btn py-0">
        <template #button-content>
          <i class="fas fa-ellipsis-v"></i>
        </template>
        <b-dropdown-item v-if="!isFolder && targetPrinter" @click.stop="$emit('print', item)">
          <span class="text-primary">
            <i class="fas fa-play-circle"></i>{{$t("Print on")}} {{ targetPrinter.name }}
          </span>
        </b-dropdown-item>
        <b-dropdown-item v-if="isCloud" @click.stop="$emit('renameItem', item)">
          <i class="fas fa-edit"></i>{{$t('Rename')}}
        </b-dropdown-item>
        <b-dropdown-item v-if="isCloud" @click.stop="$emit('moveItem', item)">
          <i class="fas fa-arrows-alt"></i>{{$t('Move')}}
        </b-dropdown-item>
        <b-dropdown-item v-if="isCloud" @click.stop="$emit('deleteItem', item)">
          <span class="text-danger"> <i class="fas fa-trash-alt"></i>{{$t('Delete')}} </span>
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileStructureItem',

  props: {
    item: {
      type: Object,
      required: true,
    },
    isCloud: {
      type: Boolean,
      default: true,
    },
    targetPrinter: {
      type: Object,
      default: null,
    },
    isMoveModal: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    selected: {
      type: Boolean,
      default: false,
    },
    selectable: {
      type: Boolean,
      default: false,
    },
  },

  data: function () {
    return {
      isSelected: this.selected,
    }
  },

  computed: {
    isFolder() {
      return !this.item.filename
    },
    isDisabled() {
      return (this.isMoveModal && !this.isFolder) || this.disabled
    },
  },

  watch: {
    isSelected(newValue) {
      this.$emit('selectedChanged', this.item, newValue)
    },
    selected(newValue) {
      this.isSelected = newValue
    },
  },
}
</script>

<style lang="sass" scoped>
.item
  display: flex
  align-items: center
  padding: .6em 1em
  border-bottom: 1px solid var(--color-divider-muted)
  &:last-child
    border-bottom: none
  &:hover
    cursor: pointer
    background-color: var(--color-hover)
  &.disabled
    opacity: .5
    &:hover
      cursor: default
      background-color: transparent
  &.move-modal
    .item-info
      .size
        text-align: right

  .item-info
    display: flex
    width: 100%
    overflow: hidden
    flex: 1
    font-size: 0.875rem
    color: var(--color-text-secondary)
    & > div
      flex: 1
      margin-left: 30px
      &:first-child
        font-size: 1rem
        color: var(--color-text-primary)
        margin-left: 0

    .thumbnail-wrapper
      flex: 0 0 32px
      display: inline-flex
      height: 32px
      border-radius: var(--border-radius-xs)
      background-color: var(--color-surface-primary)
      overflow: hidden
      align-items: center
      justify-content: center
      .thumbnail
        width: 100%
        height: 100%
        img
          height: 100%
          width: auto
      &.folder
        background: none
        font-size: 1.25em

    .filename
      display: flex
      align-items: center
      gap: .5rem
      text-overflow: ellipsis
      overflow: hidden
      white-space: nowrap
      width: 100%
      flex: 3

  .remove-button
    width: 30px
    height: 30px
    text-align: center
    line-height: 30px
    border-radius: 50%
    transition: background-color .2s ease-out
    &:hover
      background-color: var(--color-danger)
      color: var(--color-on-primary)
      cursor: pointer

  @media (max-width: 768px)
    &
      margin: 0 -16px

    .item-info
      flex-direction: column
      align-items: flex-start
      & > div
        margin-left: 0

      .size::before
        content: "Size: "
      .uploaded::before
        content: "Uploaded: "
      .created::before
        content: "Created: "
      .last-printed::before
        content: "Last print: "

.circle-indicator
  --size: 6px
  width: var(--size)
  height: var(--size)
  border-radius: var(--size)
  display: inline-block
  margin-left: 5px
  position: relative
  bottom: 1px
  background: var(--color-text-secondary)
  &.cancelled
    background: var(--color-danger)
  &.finished
    background: var(--color-success)

.checkbox-wrapper
  display: flex
  align-items: flex-start
  justify-content: flex-end
  margin-left: -.5rem
  margin-right: .5rem
  ::v-deep .custom-checkbox .custom-control-label::before
    border-radius: var(--border-radius-xs)
    border-color: var(--color-divider)
  &.isSelected
    ::v-deep .custom-checkbox .custom-control-label::before
      border-color: #00C4B4
  @media (max-width: 576px)
    display: none
</style>
