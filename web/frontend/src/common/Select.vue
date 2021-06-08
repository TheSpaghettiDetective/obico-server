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
      @click="onOptionClicked(option)"
    >{{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i></b-dropdown-item>
  </b-dropdown>
</template>

<script>
export default {
  name: 'Select',
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

<style lang="sass" scoped>
@use "~main/theme"

// bootstrap-select has this default
$tsd-dropdown-with: 220px

::v-deep .tsd-dropdown-menu
  width: $tsd-dropdown-with

::v-deep .tsd-dropdown-toggle.btn-light
  text-align: left
  width: $tsd-dropdown-with
  color: white
  background-color: rgb(var(--color-primary))
  border-radius: 0px
  border: none
  box-shadow: none

  &:hover
    color: white
    background-color: rgb(var(--color-primary))

  &[aria-expanded="true"], &:focus
    color: white !important
    background-color: rgb(var(--color-primary)) !important
    // border: none !important

  &:after
    margin-left: 0px

::v-deep .tsd-dropdown-selected-title
  width: 99%
  float: left

</style>
