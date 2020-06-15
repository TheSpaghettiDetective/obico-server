<template>
  <div class="card tsd-card">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Card"
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.tsd-card
  position: relative
</style>
