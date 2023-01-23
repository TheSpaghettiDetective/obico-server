<template>
  <div>
    <template v-if="menuExpanded === null">
      <b-dropdown-item v-for="(menu, name) in menuOptions" :key="name">
        <div
          class="d-flex justify-content-between clickable-area"
          @click.stop.prevent="menuExpanded = name"
        >
          <div>
            <i :class="menu.iconClass"></i>
            <span v-if="activeItems[name]">
              {{ activeItems[name].title }}
              <i v-if="activeItems[name].iconClass" :class="activeItems[name].iconClass"></i>
            </span>
            <span v-else>
              {{ name }}
            </span>
          </div>
          <div><i class="fas fa-chevron-right m-0"></i></div>
        </div>
      </b-dropdown-item>
    </template>
    <template v-if="menuExpanded !== null">
      <b-dropdown-item>
        <div class="clickable-area" @click.stop.prevent="menuExpanded = null">
          <i class="fas fa-chevron-left"></i>Back
        </div>
      </b-dropdown-item>
      <b-dropdown-item v-for="option in menuOptions[menuExpanded].options" :key="option.value">
        <div class="clickable-area" @click="onSelected(option)">
          <i
            class="fas fa-check text-primary"
            :style="{
              visibility: menuSelections[menuExpanded] === option.value ? 'visible' : 'hidden',
            }"
          ></i>
          {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
        </div>
      </b-dropdown-item>
    </template>
  </div>
</template>
<script>
export default {
  name: 'CascadedDropdown',
  props: {
    menuOptions: {
      type: Object,
      required: true,
    },
    menuSelections: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      menuExpanded: null,
    }
  },

  computed: {
    activeItems() {
      let items = {}
      for (const key of Object.keys(this.menuSelections)) {
        items[key] = this.menuOptions[key].options.find(
          (option) => option.value === this.menuSelections[key]
        )
      }
      return items
    },
  },

  methods: {
    onSelected(option) {
      this.$emit('menuSelectionChanged', this.menuExpanded, option)
      this.menuExpanded = null
    },
  },
}
</script>

<style></style>
