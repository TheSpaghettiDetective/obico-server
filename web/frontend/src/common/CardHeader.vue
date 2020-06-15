<template>
  <div class="card-header tsd-card-header">
    <slot />
  </div>
</template>

<script>
export default {
  name: "CardHeader"
};
</script>

<style lang="sass" scoped>
.tsd-card-header
  display: flex
  flex-flow: row nowrap
  justify-content: space-between
  align-items: center
</style>
