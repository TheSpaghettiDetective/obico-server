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
  padding: 1em

  .icon
    color: var(--color-divider)

  .message
    margin: 0
    margin-left: 0.5em
    line-height: 1.3

  @media (max-width: 768px)
    font-size: 0.8rem
</style>
