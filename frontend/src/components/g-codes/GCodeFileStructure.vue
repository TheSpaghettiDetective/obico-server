<template>
  <div class="gcodes-wrapper">
    <div class="header-panel" :class="{'without-action-buttons': !isCloud && !targetPrinter}">
      <div class="text">Name</div>
      <div class="text">Size</div>
      <div class="text">Created</div>
      <div class="text" v-if="isCloud">Last printed</div>
    </div>

    <div class="gcode-items-wrapper">
      <!-- Folders -->
      <div v-if="!searchStateIsActive">
        <div v-for="item in folders" :key="`folder_${item.id}`" class="item folder" @click="$emit('openFolder', item)">
          <div class="item-info">
            <div class="filename">
              <i class="fas fa-folder mr-1"></i>
              {{ item.name }}
            </div>
            <div class="size">{{ item.numItems }} item(s)</div>
            <div class="created">{{ item.created_at ? item.created_at.fromNow() : '-' }}</div>
            <div class="d-none d-md-block" v-if="isCloud">-</div>
          </div>
          <div v-if="isCloud">
            <b-dropdown right no-caret toggle-class="icon-btn py-0">
              <template #button-content>
                <i class="fas fa-ellipsis-v"></i>
              </template>
              <b-dropdown-item @click.stop="$emit('renameItem', item)">
                <i class="fas fa-edit"></i>Rename
              </b-dropdown-item>
              <!-- <b-dropdown-item @click.stop="$emit('moveItem', item)">
                <i class="fas fa-arrows-alt"></i>Move
              </b-dropdown-item> -->
              <b-dropdown-item @click.stop="$emit('deleteItem', item)">
                <span class="text-danger">
                  <i class="fas fa-trash-alt"></i>Delete
                </span>
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </div>
      </div>

      <!-- Files -->
      <div v-if="!searchInProgress">
        <div v-for="(item, key) in files" :key="`gcode_${key}`" class="item" @click="$emit('openFile', item)">
          <div class="item-info">
            <div class="filename">
              <i class="fas fa-file-code mr-1"></i>
              {{ item.filename }}
            </div>
            <div class="size">{{ item.filesize }}</div>
            <div class="uploaded">{{ item.created_at ? item.created_at.fromNow() : '-' }}</div>
            <div class="last-printed" v-if="isCloud">
              <span v-if="!item.print_set">-</span>
              <span v-else-if="!item.print_set.length">No prints yet</span>
              <span v-else-if="item.last_print">{{ item.last_print.ended_at ? item.last_print.ended_at.fromNow() : 'Printing...' }}</span>
              <div
                v-if="item.last_print_result"
                class="circle-indicator"
                :class="item.last_print_result"
              ></div>
            </div>
          </div>
          <div v-if="isCloud || targetPrinter">
            <b-dropdown right no-caret toggle-class="icon-btn py-0">
              <template #button-content>
                <i class="fas fa-ellipsis-v"></i>
              </template>
              <b-dropdown-item v-if="targetPrinter" @click="$mit('print', item)">
                <span class="text-primary">
                  <i class="fas fa-play-circle"></i>Print on {{ targetPrinter.name }}
                </span>
              </b-dropdown-item>
              <b-dropdown-item v-if="isCloud" @click.stop="$emit('renameItem', item)">
                <i class="fas fa-edit"></i>Rename
              </b-dropdown-item>
              <!-- <b-dropdown-item v-if="isCloud" @click.stop="$emit('moveItem', item)">
                <i class="fas fa-arrows-alt"></i>Move
              </b-dropdown-item> -->
              <b-dropdown-item v-if="isCloud" @click.stop="$emit('deleteItem', item)">
                <span class="text-danger">
                  <i class="fas fa-trash-alt"></i>Delete
                </span>
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <mugen-scroll
        v-if="isCloud"
        :v-show="!isFolderEmpty"
        :handler="() => $emit('fetchMore')"
        :should-handle="!loading"
        class="text-center"
        :scroll-container="scrollContainerId"
      >
        <div v-if="!noMoreFolders || !noMoreFiles || searchInProgress" class="py-5">
          <b-spinner label="Loading..." />
        </div>
      </mugen-scroll>

      <div v-if="!isCloud && (localFilesLoading || searchInProgress)" class="text-center py-5">
        <b-spinner label="Loading..." />
      </div>
      <div v-else>
        <!-- Placeholders -->
        <div v-if="isFolderEmpty" class="placeholder text-secondary">
          <span>Nothing here yet</span>
        </div>
        <div v-else-if="nothingFound" class="placeholder text-secondary">
          <span>Nothing found</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MugenScroll from 'vue-mugen-scroll'

export default {
  name: 'GCodeFileStructure',

  components: {
    MugenScroll,
  },

  props: {
    isCloud: Boolean,
    searchStateIsActive: Boolean,
    searchInProgress: Boolean,
    folders: Array,
    files: Array,
    targetPrinter: Object || null,
    isFolderEmpty: Boolean,
    nothingFound: Boolean,
    loading: Boolean,
    scrollContainerId: String || null,
    noMoreFolders: Boolean,
    noMoreFiles: Boolean,
    localFilesLoading: Boolean,
  },
}
</script>

<style lang="sass" scoped>
.gcodes-wrapper
  background-color: var(--color-surface-secondary)
  padding: 1em 2em
  border-radius: var(--border-radius-lg)

.header-panel
  display: flex
  padding: 1em calc(1em + 30px) 1em 1em
  border-bottom: 1px solid var(--color-divider)
  font-weight: bold
  &.without-action-buttons
    padding-right: 1em

  & > div
    flex: 1
    display: flex
    justify-content: space-between
    margin-left: 30px
    align-items: center
    font-size: 1rem

    &:first-child
      margin-left: 0
      flex: 3

  @media (max-width: 768px)
    &
      display: none

.gcode-items-wrapper
  .item
    display: flex
    align-items: center
    padding: .6em 1em
    border-bottom: 1px solid var(--color-divider-muted)

    &:not(.folder)
      &:last-child
        border-bottom: none

    &:hover
      cursor: pointer
      background-color: var(--color-hover)

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

      .filename
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

.placeholder
  margin: 5rem 0
  text-align: center
  &.text-secondary *
    color: var(--color-text-secondary)
</style>