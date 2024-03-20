<template>
  <div>
    <template v-if="menuExpanded === null">
      <b-dropdown-item
        v-for="option in menuOptions"
        :key="option.key"
        :href="option.href"
        @click="onClick(option)"
      >
        <div
          v-if="option.expandable"
          class="d-flex justify-content-between clickable-area"
          @click.stop.prevent="menuExpanded = option.key"
        >
          <div>
            <i v-if="option.icon" :class="option.icon"></i>
            <svg v-else-if="option.svgIcon" class="custom-svg-icon">
              <use :href="`#${option.svgIcon}`" />
            </svg>
            <span>{{ option.title }}</span>
          </div>
          <div><i class="fas fa-chevron-right m-0"></i></div>
        </div>
        <div v-else class="d-flex justify-content-between clickable-area">
          <div :class="option.customMenuOptionClass">
            <i v-if="option.icon" :class="option.icon"></i>
            <svg v-else-if="option.svgIcon" class="custom-svg-icon">
              <use :href="`#${option.svgIcon}`" />
            </svg>

            <span>{{ option.title }}</span>
          </div>
        </div>
      </b-dropdown-item>
    </template>
    <template v-if="menuExpanded !== null">
      <b-dropdown-item>
        <div class="clickable-area" @click.stop.prevent="menuExpanded = null">
          <i class="fas fa-chevron-left"></i>{{$t("Back")}}
        </div>
      </b-dropdown-item>
      <b-dropdown-divider />

      <div v-if="menuExpanded === 'sorting'">
        <slot name="sorting"></slot>
      </div>
      <div v-if="menuExpanded === 'filtering'">
        <slot name="filtering"></slot>
      </div>
      <div v-if="menuExpanded === 'storage'">
        <slot name="storage"></slot>
      </div>
      <div v-if="menuExpanded === 'grouping'">
        <slot name="grouping"></slot>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'CascadedDropdown',

  props: {
    menuOptions: {
      type: Array,
      required: true,
    },
  },

  data: function () {
    return {
      menuExpanded: null,
    }
  },

  methods: {
    resetMenuExpanded() {
      this.menuExpanded = null
    },
    onClick(menuOption) {
      if (menuOption.callback) {
        this.$emit('menuOptionClicked', menuOption.key)
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.custom-svg-icon
  height: 1.125rem
  width: 1.125rem
</style>
