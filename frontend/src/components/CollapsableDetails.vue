<template>
  <div>
    <!-- Content -->
    <b-collapse v-model="expanded">
      <slot></slot>
    </b-collapse>

    <!-- Toggle -->
    <button
      class="collapse-toggle"
      :class="expanded ? 'opened' : 'closed'"
      @click="expanded = !expanded"
    >
      <span v-if="expanded">{{ $t("Show less") }}</span>
      <span v-else>{{ $t("Show more") }}</span>
      <font-awesome-icon :icon="['fas', 'chevron-down']" :class="{ rotated: expanded }" />
    </button>
  </div>
</template>

<script>
export default {
  name: 'CollapsableDetails',

  data() {
    return {
      expanded: false,
    }
  },
}
</script>

<style lang="sass" scoped>
.collapse-toggle
  width: 100%
  font-weight: bold
  display: flex
  align-items: center
  justify-content: center
  gap: .5rem
  background: none
  border: none
  color: var(--color-text-primary)
  margin-top: .5rem
  svg
    transition: all .3s ease-in-out
    &.rotated
      transform: rotate(180deg)
</style>
