<template>
  <div class="search-wrapper">
    <div class="search-icon">
      <i class="fas fa-search"></i>
    </div>
    <input
      type="text"
      placeholder="Search"
      :value="value"
      @input="$emit('input', $event.target.value)"
    >
  </div>
</template>

<script>
  export default {
    name: 'SearchInput',

    props: {
      value: {
        type: String,
        default: ''
      },
    },
  }
</script>

<style lang="sass" scoped>
  @use "~main/theme"

  .search-wrapper
    position: relative

    .search-icon
      height: 100%
      display: flex
      flex-direction: column
      justify-content: center
      position: absolute
      top: 0
      left: .5em
      opacity: .8

    input
      background-color: rgb(var(--color-input-dark-bg))
      border: 1px solid rgb(var(--color-input-dark-bg))
      color: rgb(var(--color-main-text))
      outline: none
      padding: .2em .5em .2em 2em
      width: 100%
      height: 100%

      &:focus
        border-color: rgb(var(--color-white))
</style>