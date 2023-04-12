<template>
  <div class="widget">
    <div class="widget-title">
      <slot name="title"></slot>
    </div>
    <div class="widget-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WidgetTemplate',
}
</script>

<style lang="sass" scoped>
.widget
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)
  margin-bottom: 15px
  &:last-of-type
    margin-bottom: 0
  .widget-title
    padding: 6px 12px
    font-size: 14px
    color: var(--color-text-secondary)
  .widget-content
    padding: 1.5rem 2rem 1rem
</style>
