<template>
  <b-dropdown :toggle-class="'btn-light obico-dropdown-toggle'" :menu-class="'obico-dropdown-menu'">
    <template #button-content>
      <div class="obico-dropdown-selected-title">
        {{ selected_title }} <i v-if="selected.iconClass" :class="selected.iconClass"></i>
      </div>
    </template>
    <b-dropdown-item
      v-for="option in options"
      :key="option.value"
      :active="value == option.value"
      @click="onOptionClicked(option)"
      >{{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i
    ></b-dropdown-item>
  </b-dropdown>
</template>

<script>
export default {
  name: 'SelectInput',

  props: {
    options: {
      type: Array,
      required: true,
    },
    value: {
      type: String || Number,
      default: null,
    },
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
    },
  },
  methods: {
    onOptionClicked(option) {
      this.$emit('input', option.value)
    },
  },
}
</script>

<style lang="sass" scoped>
// bootstrap-select has this default
$obico-dropdown-with: 220px

::v-deep .obico-dropdown-menu
  width: $obico-dropdown-with

::v-deep .obico-dropdown-toggle.btn-light
  text-align: left
  width: $obico-dropdown-with
  color: white
  background-color: var(--color-primary)
  border-radius: 0px
  border: none
  box-shadow: none

  &:hover
    color: white
    background-color: var(--color-primary)

  &[aria-expanded="true"], &:focus
    color: white !important
    background-color: var(--color-primary) !important
    // border: none !important

  &:after
    margin-left: 0px

::v-deep .obico-dropdown-selected-title
  width: 99%
  float: left
</style>
