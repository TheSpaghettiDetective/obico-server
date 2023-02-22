<template>
  <page-layout>
    <!-- Top bar -->
    <template #topBarRight>
      <div class="action-panel">
        <!-- Sorting -->
        <b-dropdown right no-caret toggle-class="action-btn icon-btn" title="Sort By">
          <template #button-content>
            <i class="fas fa-sort-amount-down"></i>
          </template>
          <sorting-dropdown
            :local-storage-prefix="sortingLocalStoragePrefix"
            :sorting-options="sortingOptions"
            :sorting-value="sortingValue"
            @onSortingUpdated="onSortingUpdated"
          />
        </b-dropdown>
        <!-- Filtering -->
        <b-dropdown
          right
          no-caret
          toggle-class="action-btn icon-btn"
          menu-class="scrollable"
          title="Filter"
        >
          <template #button-content>
            <i class="fas fa-filter"></i>
          </template>
          <filtering-dropdown
            ref="filteringDropdown1"
            :local-storage-prefix="filterLocalStoragePrefix"
            :filter-options="filterOptions"
            :filter-values="filterValues"
            :filter-update-mixin="filterUpdateMixin"
            @onFilterUpdated="onFilterUpdated"
          />
        </b-dropdown>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="[
              {
                key: 'sorting',
                icon: 'fas fa-sort-amount-down',
                title: `Sort`,
                expandable: true,
              },
              {
                key: 'filtering',
                icon: 'fas fa-filter',
                title: `Filter`,
                expandable: true,
              },
            ]"
          >
            <template #sorting>
              <sorting-dropdown
                :local-storage-prefix="sortingLocalStoragePrefix"
                :sorting-options="sortingOptions"
                :sorting-value="sortingValue"
                @onSortingUpdated="onSortingUpdated"
              />
            </template>
            <template #filtering>
              <filtering-dropdown
                ref="filteringDropdown2"
                :local-storage-prefix="filterLocalStoragePrefix"
                :filter-options="filterOptions"
                :filter-values="filterValues"
                :filter-update-mixin="filterUpdateMixin"
                @onFilterUpdated="onFilterUpdated"
              />
            </template>
          </cascaded-dropdown>
        </b-dropdown>
      </div>
    </template>

    <!-- Page content -->
    <template #content>
      <active-filter-notice :filter-values="filterValues" @onShowAllClicked="resetFilters" />

      <!-- Prints list -->
      <b-container>
        <b-row>
          <b-col>
            <div v-if="prints.length && !loading" class="prints-summary">
              <div class="summary-item">
                <div class="icon">
                  <i class="fas fa-hashtag"></i>
                </div>
                <div class="info">
                  <div class="title">Prints done</div>
                  <div class="value">
                    {{ stats.total_print_count }} (<span class="text-success">{{
                      stats.total_succeeded_print_count
                    }}</span>
                    / <span class="text-danger">{{ stats.total_cancelled_print_count }}</span
                    >)
                  </div>
                </div>
              </div>
              <div class="summary-item">
                <div class="icon">
                  <i class="far fa-clock"></i>
                </div>
                <div class="info">
                  <div class="title">Total print time</div>
                  <div class="value">{{ totalPrintTimeFormatted }}</div>
                </div>
              </div>
              <div class="summary-item">
                <div class="icon">
                  <i class="fas fa-ruler-horizontal"></i>
                </div>
                <div class="info">
                  <div class="title">
                    <help-widget
                      id="filament-used-may-be-incorrect"
                      :highlight="false"
                      :show-close-button="false"
                    >
                      Filament used
                    </help-widget>
                  </div>
                  <div class="value">{{ totalFilamentUsedFormatted }}m</div>
                </div>
              </div>
              <!-- <div class="btn-wrapper">
                <a class="btn btn-secondary" :href="`/stats/`">
                  Full stats
                  <i class="fas fa-arrow-right"></i>
                </a>
              </div> -->
            </div>
          </b-col>
        </b-row>
        <b-row>
          <b-col v-if="prints.length || loading">
            <print-history-item
              v-for="print of prints"
              :key="print.id"
              :print="print"
              class="print-item"
            ></print-history-item>
            <mugen-scroll :handler="fetchMoreData" :should-handle="!loading">
              <loading-placeholder v-if="!noMoreData" />
            </mugen-scroll>
          </b-col>
          <b-col v-else class="text-center my-5">No prints found</b-col>
        </b-row>
      </b-container>

      <!-- Date picker for filter by time period -->
      <date-picker-modal ref="datePickerModal" @picked="onDatesPicked" />
    </template>
  </page-layout>
</template>

<script>
import moment from 'moment'
import axios from 'axios'
import MugenScroll from 'vue-mugen-scroll'
import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import PageLayout from '@src/components/PageLayout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import SortingDropdown, { restoreSortingValue } from '@src/components/SortingDropdown'
import FilteringDropdown, {
  restoreFilterValues,
  getFilterParams,
} from '@src/components/FilteringDropdown'
import ActiveFilterNotice from '@src/components/ActiveFilterNotice'
import PrintHistoryItem from '@src/components/prints/PrintHistoryItem.vue'
import DatePickerModal from '@src/components/DatePickerModal.vue'
import { user } from '@src/lib/page-context'
import HelpWidget from '@src/components/HelpWidget.vue'

const PAGE_SIZE = 24

const SortingLocalStoragePrefix = 'printsSorting'
const SortingOptions = {
  options: [{ title: 'Date', key: 'date' }],
  default: { sorting: 'date', direction: 'desc' },
}

const DateParamFormat = 'YYYY-MM-DD'
const FilterLocalStoragePrefix = 'printsFiltering'
const FilterOptions = {
  timePeriod: {
    title: 'Time Period',
    buildQueryParam: (val, dateFrom, dateTo, user) => {
      let params = {}
      const today = new Date()
      const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()))
      const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      const firstDayOfYear = new Date(today.getFullYear(), 0, 1)

      switch (val) {
        case 'this_week':
          params = { from_date: moment(firstDayOfWeek).format(DateParamFormat) }
          break
        case 'this_month':
          params = { from_date: moment(firstDayOfMonth).format(DateParamFormat) }
          break
        case 'this_year':
          params = { from_date: moment(firstDayOfYear).format(DateParamFormat) }
          break
        case 'custom':
          if (dateFrom) {
            params['from_date'] = moment(dateFrom).format(DateParamFormat)
          }
          if (dateTo) {
            params['to_date'] = moment(dateTo).format(DateParamFormat)
          }
          break
        default:
          return {}
      }
      params['from_date'] = params['from_date'] || moment(user.date_joined).format(DateParamFormat)
      params['to_date'] = params['to_date'] || moment(new Date()).format(DateParamFormat)
      params['timezone'] = Intl.DateTimeFormat().resolvedOptions().timeZone
      return params
    },
    values: [
      { key: 'none', title: 'All' },
      { key: 'this_week', title: 'This Week' },
      { key: 'this_month', title: 'This Month' },
      { key: 'this_year', title: 'This Year' },
      { key: 'custom', title: 'Custom' },
    ],
    default: 'none',
  },
  printStatus: {
    title: 'Print Status',
    queryParam: 'filter',
    values: [
      { key: 'none', title: 'All' },
      { key: 'finished', title: 'Finished' },
      { key: 'cancelled', title: 'Cancelled' },
    ],
    default: 'none',
  },
  feedbackNeeded: {
    title: 'Feedback Needed',
    queryParam: 'feedback_needed',
    values: [
      { key: 'none', title: 'All' },
      { key: 'need_alert_overwrite', title: 'Review Needed' },
      { key: 'need_print_shot_feedback', title: 'Focused Feedback Needed' },
    ],
    default: 'none',
  },
  printers: {
    title: 'Printers',
    queryParam: 'filter_by_printer_ids',
    multiple: true,
    values: [
      { key: 'none', title: 'All', includesAll: true },
      // Other options are added on printers fetch
    ],
    default: 'none',
  },
}

export default {
  name: 'PrintHistoryPage',

  components: {
    MugenScroll,
    PageLayout,
    CascadedDropdown,
    DatePickerModal,
    SortingDropdown,
    FilteringDropdown,
    ActiveFilterNotice,
    PrintHistoryItem,
    HelpWidget,
  },

  data: function () {
    return {
      stats: {},
      prints: [],
      loading: false,
      noMoreData: false,
      user: null,

      // Sorting
      sortingLocalStoragePrefix: SortingLocalStoragePrefix,
      sortingOptions: SortingOptions,
      sortingValue: restoreSortingValue(SortingLocalStoragePrefix, SortingOptions),

      // Filtering
      filterLocalStoragePrefix: FilterLocalStoragePrefix,
      filterOptions: FilterOptions,
      filterValues: restoreFilterValues(FilterLocalStoragePrefix, FilterOptions),
    }
  },

  computed: {
    totalPrintTimeFormatted() {
      const duration = moment.duration(this.stats.total_print_time, 'seconds')
      const days = Math.floor(duration.asDays())
      const hours = duration.hours()
      const minutes = duration.minutes()

      let result = ''

      if (days !== 0) {
        result += `${days}d `
      }
      if (days !== 0 || hours !== 0) {
        result += `${hours}h `
      }

      result += `${minutes}m`
      return result
    },
    totalFilamentUsedFormatted() {
      if (!this.stats?.total_filament_used) {
        return 0
      }
      const meters = this.stats.total_filament_used / 1000
      return Math.round(meters * 100) / 100
    },
    defaultStatsParams() {
      return {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        from_date: moment(this.user.date_joined).format(DateParamFormat),
        to_date: moment(new Date()).format(DateParamFormat),
        group_by: 'year',
      }
    },
  },

  created() {
    this.user = user()
    this.updateCustomPeriodFilterSubtitle()

    // get printers first to remove deleted/archived printers from filtering before fetching prints
    axios
      .get(urls.printers(), {
        params: {
          with_archived: false,
        },
      })
      .then((response) => {
        response.data.forEach((p) => {
          this.filterOptions.printers.values.push({
            key: String(p.id),
            title: p.name,
          })
        })

        // remove deleted/archived printers from applied filter
        if (this.filterValues.printers !== 'none') {
          const validPrinterIds = response.data.map((p) => String(p.id))
          this.filterValues.printers = this.filterValues.printers.filter((v) =>
            validPrinterIds.includes(v)
          )
          setLocalPref(`${FilterLocalStoragePrefix}-printers`, this.filterValues.printers)
        }

        this.refetchData()
      })
  },

  methods: {
    fetchMoreData() {
      if (this.noMoreData) {
        return
      }
      this.loading = true
      axios
        .get(urls.prints(), {
          params: {
            start: this.prints.length,
            limit: PAGE_SIZE,
            ...getFilterParams(
              this.filterOptions,
              this.filterValues,
              this.customFilterParamsBuilder
            ),
            sorting: `${this.sortingValue.sorting.key}_${this.sortingValue.direction.key}`,
          },
        })
        .then((response) => {
          this.loading = false
          this.noMoreData = response.data.length < PAGE_SIZE
          this.prints.push(...response.data.map((data) => normalizedPrint(data)))
        })
        .catch((error) => {
          this._showErrorPopup(error)
        })
    },
    refetchData() {
      this.prints = []
      this.noMoreData = false
      this.fetchMoreData()
      this.fetchStats()
    },
    fetchStats() {
      axios
        .get(urls.stats(), {
          params: {
            ...this.defaultStatsParams,
            ...getFilterParams(
              this.filterOptions,
              this.filterValues,
              this.customFilterParamsBuilder
            ),
          },
        })
        .then((response) => {
          this.stats = response.data
        })
        .catch((error) => {
          this._showErrorPopup(error)
        })
    },

    // Sorting
    onSortingUpdated(sortingValue) {
      this.sortingValue = sortingValue
      this.refetchData()
    },

    // Filtering
    onFilterUpdated(filterOptionKey, filterOptionValue) {
      this.filterValues[filterOptionKey] = filterOptionValue
      this.refetchData()
    },
    resetFilters() {
      for (const key of Object.keys(this.filterValues)) {
        this.filterValues[key] = 'none'
        setLocalPref(`${FilterLocalStoragePrefix}-${key}`, 'none')
      }
      this.updateCustomPeriodFilterSubtitle()
      this.refetchData()
    },
    // custom logic for time period filters:
    getCurrentDateFrom() {
      return getLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateFrom`) || null
    },
    getCurrentDateTo() {
      return getLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateTo`) || null
    },
    filterUpdateMixin(filterOptionKey, filterValueKey) {
      if (filterOptionKey === 'timePeriod') {
        if (filterValueKey === 'custom') {
          if (this.filterValues.timePeriod !== 'custom') {
            this.$refs.datePickerModal.show()
          } else {
            const initDateFrom = this.getCurrentDateFrom()
            const initDateTo = this.getCurrentDateTo()
            this.$refs.datePickerModal.show(initDateFrom, initDateTo)
          }
          return
        } else {
          this.$nextTick(() => {
            this.updateCustomPeriodFilterSubtitle()
          })
        }
      }
      return true
    },
    onDatesPicked(dateFrom, dateTo) {
      if (!dateFrom && !dateTo) {
        return
      }
      this.filterValues.timePeriod = 'custom'
      setLocalPref(`${FilterLocalStoragePrefix}-timePeriod`, 'custom')
      setLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateFrom`, dateFrom)
      setLocalPref(`${FilterLocalStoragePrefix}-timePeriod-dateTo`, dateTo)
      this.updateCustomPeriodFilterSubtitle()
      this.refetchData()
    },
    customFilterParamsBuilder(filterOptionKey, filterValueKey) {
      if (filterOptionKey === 'timePeriod') {
        return this.filterOptions[filterOptionKey].buildQueryParam(
          filterValueKey,
          this.getCurrentDateFrom(),
          this.getCurrentDateTo(),
          this.user
        )
      }
    },
    updateCustomPeriodFilterSubtitle() {
      let newTitle = ''
      if (this.filterValues.timePeriod === 'custom') {
        // variants:
        // Feb 15, 2023 — Feb 16, 2023
        // Feb 15, 2023 and later
        // Until Feb 16, 2023
        const dateFormat = 'MMM D, YYYY'
        const currentDateFrom = this.getCurrentDateFrom()
        const currentDateTo = this.getCurrentDateTo()
        const dateFromFormatted = currentDateFrom
          ? moment(currentDateFrom).format(dateFormat)
          : 'Until'
        const dateToFormatted = currentDateTo
          ? moment(currentDateTo).format(dateFormat)
          : 'and later'

        newTitle = `${dateFromFormatted}${
          currentDateFrom && currentDateTo ? ' - ' : ' '
        }${dateToFormatted}`
      }

      const index = this.filterOptions.timePeriod.values.findIndex((v) => v.key === 'custom')
      this.filterOptions.timePeriod.values[index].subtitle = newTitle

      this.$refs.filteringDropdown1 && this.$refs.filteringDropdown1.$forceUpdate()
      this.$refs.filteringDropdown2 && this.$refs.filteringDropdown2.$forceUpdate()
    },
  },
}
</script>

<style lang="sass" scoped>
.print-item
  margin-bottom: 10px

.prints-summary
  margin-bottom: var(--gap-between-blocks)
  border: 1px solid var(--color-divider)
  border-radius: var(--border-radius-lg)
  padding: 1.5rem 2rem
  display: flex
  justify-content: space-around
  align-items: center
  .summary-item
    display: flex
    align-items: center
    gap: 1rem
  .icon
    font-size: 1.5rem
    color: var(--color-divider)
  .value
    font-weight: bold
  .btn
    display: inline-flex
    gap: .5rem
    align-items: center
    justify-content: center
    .fa-arrow-right
      font-size: .8em

  @media (max-width: 768px)
    flex-direction: column
    align-items: normal
    gap: .25rem
    padding: 1rem

    .summary-item
      gap: 0
      .icon
        font-size: 1rem
        width: 2rem
        text-align: center
      .info
        flex: 1
        display: flex
        justify-content: space-between

    .btn-wrapper
      text-align: center
    .btn
      margin-top: 1rem
      font-size: .875rem
</style>
