<template>
  <div class="search-wrapper">
    <div class="search-icon">
      <i class="fas fa-search"></i>
    </div>
    <input
      type="text"
      class="dark"
      :placeholder="$t('Search')"
      :value="value"
      @input="$emit('input', $event.target.value)"
      @focus="$emit('focus')"
      @blur="$emit('blur')"
    />
  </div>
</template>

<script>
export default {
  name: 'SearchInput',

  props: {
    value: {
      type: String,
      default: '',
    },
  },
}
</script>

<style lang="sass" scoped>
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
    padding: .2em .5em .2em 2em
    width: 100%
    height: 100%
    font-size: 16px
</style>
