<template>
  <a href="#" class="btn btn-outline-primary" @click="handleClick">
    {{ message }}
  </a>
</template>

<script>
export default {
  name: 'QuickButtonComponent',
  props: {
    message: {
      type: String,
      required: true,
    },
  },
  methods: {
    handleClick(event) {
      this.$emit('click', event)
    },
  },
}
</script>

<style lang="sass" scoped>
.btn
  width: auto
  max-width: 100%
  white-space: normal
  text-align: center
  padding: 0.5rem 1rem
  hyphens: auto
  word-wrap: break-word
  overflow-wrap: break-word
</style>
