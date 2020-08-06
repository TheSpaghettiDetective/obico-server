<template>
  <b-dropdown
    :toggle-class="'btn-light tsd-dropdown-toggle'"
    :menu-class="'tsd-dropdown-menu'"
  >
    <template v-slot:button-content>
      <div class="tsd-dropdown-selected-title">{{ selected_title }} <i v-if="selected.iconClass" :class="selected.iconClass"></i></div>
    </template>
    <b-dropdown-item
      v-for="option in options"
      :key="option.value"
      :active="value == option.value"
      :active-class="'tsd-dropdown-active-item'"
      @click="onOptionClicked(option)"
    >{{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i></b-dropdown-item>
  </b-dropdown>
</template>

<script>
export default {
  name: 'TSDSelect',
  props: ['options', 'value'],
  methods: {
    onOptionClicked(option) {
      this.$emit('input', option.value)
    }
  },
  computed: {
    selected() {
      if (this.options) {
        return this.options.find((option) => option.value == this.value)
      }
      return null
    },
    selected_title() {
      let cur = this.selected
      return cur.selected_title || cur.title
    }
  }
}
</script>

<style lang="sass">
@use "~main/theme"

// bootstrap-select has this default
$tsd-dropdown-with: 220px

.tsd-dropdown-toggle
  text-align: left
  width: $tsd-dropdown-with

.tsd-dropdown-menu
  width: $tsd-dropdown-with

.tsd-dropdown-toggle
  color: white
  background-color: theme.$blue
  border-radius: 0px
  border: none
  text-align: left

  &:hover
    color: white
    background-color: theme.$blue

  &:after
    margin-left: 0px

.tsd-dropdown-selected-title
  width: 99%
  float: left

.tsd-dropdown-active-item
  color: white
  background-color: theme.$blue

</style>
