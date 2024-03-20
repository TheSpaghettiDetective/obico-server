<template>
  <div v-if="shouldShowFilterWarning" class="active-filter-notice">
    <div class="filter">
      <i class="fas fa-filter mr-2"></i>
      {{$t("Filters applied")}}
    </div>
    <div class="action-btn" @click="$emit('onShowAllClicked')">{{ $t("SHOW ALL") }}</div>
  </div>
</template>

<script>
export default {
  name: 'ActiveFilterNotice',

  props: {
    filterValues: {
      type: Object,
      required: true,
    },
  },

  computed: {
    activeFilters() {
      return Object.values(this.filterValues).filter((v) => v !== 'none')
    },
    shouldShowFilterWarning() {
      return this.activeFilters.length !== 0
    },
  },
}
</script>

<style lang="sass" scoped>
.active-filter-notice
  display: flex
  align-items: center
  justify-content: space-between
  padding: 0.5rem 1rem
  background-color: var(--color-surface-secondary)
  margin: calc(-1 * var(--gap-between-blocks)) -15px var(--gap-between-blocks)
  .filter
    color: var(--color-primary)
  .action-btn
    color: var(--color-text-primary)
    cursor: pointer

  @media (max-width: 768px)
    font-size: .875rem
    margin-left: 0
    margin-right: 0
</style>
