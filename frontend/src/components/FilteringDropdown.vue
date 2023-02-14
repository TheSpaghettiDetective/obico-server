<template>
  <div>
    <div v-for="(option, key, index) in filterOptions" :key="key">
      <b-dropdown-divider v-if="index !== 0" />
      <b-dropdown-text class="small text-secondary">{{
        option.title.toUpperCase()
      }}</b-dropdown-text>
      <b-dropdown-item
        v-for="val in option.values"
        :key="`f_${key}_${val.key}`"
        @click.native.capture.stop.prevent="
          updateFiltering({ filterOptionKey: key, filterValueKey: val.key })
        "
      >
        <div class="dropdown-text-group">
          <i
            class="fas fa-check text-primary"
            :class="{
              'checkmark-muted':
                option.multiple &&
                !val.includesAll &&
                (!Array.isArray(filterValues[key]) || !filterValues[key].includes(val.key)),
            }"
            :style="{
              visibility:
                (Array.isArray(filterValues[key]) && filterValues[key].includes(val.key)) ||
                filterValues[key] === val.key ||
                (option.multiple && !val.includesAll)
                  ? 'visible'
                  : 'hidden',
            }"
          ></i>
          <div class="text">
            {{ val.title }}
            <div v-if="val.subtitle" class="subtitle">
              {{ val.subtitle }}
            </div>
          </div>
        </div>
      </b-dropdown-item>
    </div>
  </div>
</template>

<script>
import { getLocalPref, setLocalPref } from '@src/lib/pref'

export default {
  name: 'FilteringDropdown',

  props: {
    localStoragePrefix: {
      type: String,
      required: true,
    },
    filterOptions: {
      type: Object,
      required: true,
    },
    filterValues: {
      type: Object,
      required: true,
    },
    filterUpdateMixin: {
      type: Function,
      default: null,
    },
  },

  methods: {
    updateFiltering({ filterOptionKey, filterValueKey }) {
      if (this.filterUpdateMixin) {
        const result = this.filterUpdateMixin(filterOptionKey, filterValueKey)
        if (!result) {
          return
        }
      }

      const filterOption = this.filterOptions[filterOptionKey]
      const filterValue = filterOption.values.find((v) => v.key === filterValueKey)

      const currentFilterValue = this.filterValues[filterOptionKey]
      let newFilterValue

      if (filterOption.multiple) {
        if (filterValue.includesAll) {
          newFilterValue = filterValue.key
        } else {
          if (Array.isArray(currentFilterValue)) {
            if (currentFilterValue.includes(filterValueKey)) {
              newFilterValue = currentFilterValue.filter((v) => v !== filterValueKey)
              if (!newFilterValue.length) {
                // if user unselects all — switch to "All" option if exists
                newFilterValue = filterOption.values.find((v) => v.includesAll)?.key || []
              }
            } else {
              newFilterValue = [...currentFilterValue, filterValueKey]
            }
          } else {
            newFilterValue = [filterValueKey]
          }
        }
      } else {
        newFilterValue = filterValueKey
      }

      if (newFilterValue === currentFilterValue) {
        return // nothing changed
      }

      setLocalPref(`${this.localStoragePrefix}-${filterOptionKey}`, newFilterValue)
      this.$emit('onFilterUpdated', filterOptionKey, newFilterValue)
    },
  },
}

export const restoreFilterValues = (localStoragePrefix, filterOptions) => {
  let values = {}
  for (const [key, option] of Object.entries(filterOptions)) {
    const val = String(getLocalPref(`${localStoragePrefix}-${key}`, option.default))
    if (option.multiple) {
      const allOption = option.values.find((v) => v.includesAll)
      if (val === allOption.key) {
        values[key] = val
      } else {
        values[key] = val.split(',')
      }
    } else {
      values[key] = val
    }
  }
  return values
}

export const getFilterParams = (filterOptions, filterValues, customFilterParamsBuilder) => {
  let params = {}

  for (const [key, val] of Object.entries(filterValues)) {
    const filterOption = filterOptions[key]

    if (!filterOption.buildQueryParam) {
      if (val !== 'none') {
        params[filterOption.queryParam] = val
      }
    } else {
      const customParams = customFilterParamsBuilder && customFilterParamsBuilder(key, val)
      if (customParams) {
        params = { ...params, ...customParams }
      }
    }
  }
  return params
}
</script>

<style lang="sass" scoped>
.checkmark-muted
  color: var(--color-divider) !important
</style>
