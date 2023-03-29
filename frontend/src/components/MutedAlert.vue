<template>
  <div class="alert-wrapper">
    <div class="icon">
      <i class="fas fa-info-circle"></i>
    </div>
    <p class="message">
      <slot></slot>
    </p>
  </div>
</template>

<script>
export default {
  name: 'MutedAlert',
}
</script>

<style lang="sass" scoped>
.alert-wrapper
  border: 1px solid var(--color-divider)
  border-radius: var(--border-radius-md)
  display: flex
  align-items: center
  padding: 1rem 1.5rem
  margin-bottom: var(--gap-between-blocks)

  .icon
    color: var(--color-divider)

  .message
    margin: 0
    margin-left: 0.5em
</style>
