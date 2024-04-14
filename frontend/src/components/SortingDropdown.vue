<template>
  <div>
    <b-dropdown-text class="small text-secondary">{{ $t("SORT BY") }}</b-dropdown-text>
    <b-dropdown-item
      v-for="sorting in sortingOptions.options"
      :key="`s_${sorting.key}`"
      @click.native.capture.stop.prevent="updateSorting({ sorting })"
    >
      <i
        class="fas fa-check text-primary"
        :style="{
          visibility: sortingValue.sorting.key === sorting.key ? 'visible' : 'hidden',
        }"
      ></i>
      {{ sorting.title }}
    </b-dropdown-item>

    <b-dropdown-divider />

    <b-dropdown-text class="small text-secondary">{{ $t("DIRECTION") }}</b-dropdown-text>
    <b-dropdown-item
      v-for="direction in sortingDirections"
      :key="`d_${direction.key}`"
      @click.native.capture.stop.prevent="updateSorting({ direction })"
    >
      <i
        class="fas fa-check text-primary"
        :style="{
          visibility: sortingValue.direction.key === direction.key ? 'visible' : 'hidden',
        }"
      ></i>
      {{ direction.title }}
    </b-dropdown-item>
  </div>
</template>

<script>
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import i18n from '@src/i18n/i18n.js'

const SortingDirections = [
  { key: 'asc', title: `${i18n.t('Ascending')}` },
  { key: 'desc', title: `${i18n.t('Descending')}` },
]

export default {
  name: 'SortingDropdown',

  props: {
    localStoragePrefix: {
      type: String,
      required: true,
    },
    sortingOptions: {
      type: Object,
      required: true,
    },
    sortingValue: {
      type: Object,
      required: true,
    },
  },

  data: function () {
    return {
      sortingDirections: SortingDirections,
    }
  },

  methods: {
    updateSorting({ sorting, direction }) {
      if (sorting && sorting.key !== this.sortingValue.sorting.key) {
        setLocalPref(`${this.localStoragePrefix}-sorting`, sorting.key)
        this.$emit('onSortingUpdated', { ...this.sortingValue, sorting: sorting })
        return
      }
      if (direction && direction.key !== this.sortingValue.direction.key) {
        setLocalPref(`${this.localStoragePrefix}-direction`, direction.key)
        this.$emit('onSortingUpdated', { ...this.sortingValue, direction: direction })
        return
      }
    },
  },
}

export const restoreSortingValue = (localStoragePrefix, sortingOptions) => {
  const sortingKey = getLocalPref(`${localStoragePrefix}-sorting`, sortingOptions.default.sorting)
  const directionKey = getLocalPref(
    `${localStoragePrefix}-direction`,
    sortingOptions.default.direction
  )

  return {
    sorting: sortingOptions.options.find((s) => s.key === sortingKey),
    direction: SortingDirections.find((d) => d.key === directionKey),
  }
}
</script>
