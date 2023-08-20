<template>
  <div class="wrapper">
    <draggable
      v-model="currentItems"
      ghost-class="ghost"
      handle=".handle"
      @start="dragging = true"
      @end="dragging = false"
    >
      <div v-for="item in currentItems" :key="item.id" class="item">
        <div class="handle">
          <i class="fas fa-grip-lines"></i>
        </div>
        <div class="title">
          <span>{{ getTitle(item.id) }}</span>
        </div>
        <div class="switch">
          <div class="custom-control custom-switch">
            <input
              :id="'widget-toggle-' + item.id"
              type="checkbox"
              name="pause_on_failure"
              class="custom-control-input update-printer"
              :checked="item.enabled"
              @click="toggleItemEnabled(item)"
            />
            <label
              class="custom-control-label"
              :for="'widget-toggle-' + item.id"
              style="font-size: 1rem"
            ></label>
          </div>
        </div>
      </div>
    </draggable>
    <input id="sorting-config" ref="sortingConfig" type="hidden" />
  </div>
</template>

<script>
import draggable from 'vuedraggable'

export default {
  name: 'ReorderModal',

  components: {
    draggable,
  },

  props: {
    items: {
      type: Array,
      required: true,
    },
    extraInfo: {
      type: Array,
      required: true,
    },
  },

  data() {
    return {
      dragging: false,
      currentItems: [],
    }
  },

  watch: {
    dragging(newVal, oldVal) {
      if (!newVal) {
        this.saveNewOrder()
      }
    },
  },

  created() {
    this.currentItems = JSON.parse(JSON.stringify(this.items))
  },

  mounted() {},

  methods: {
    getTitle(id) {
      return this.extraInfo.find((item) => item.id === id).title
    },
    toggleItemEnabled(item) {
      item.enabled = !item.enabled
      this.saveNewOrder()
    },
    saveNewOrder() {
      this.$refs.sortingConfig.value = JSON.stringify(this.currentItems)
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  gap: 1rem

.item
  display: flex
  align-items: center
  gap: .5rem
  border-bottom: 1px solid var(--color-divider-muted)
  padding: .5rem 0
  .handle
    font-size: 1.25rem
    color: var(--color-text-secondary)
    cursor: move
  .title
    flex: 1
  &.ghost
    opacity: .1
</style>
