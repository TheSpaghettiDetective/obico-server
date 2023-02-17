<template>
  <page-layout>
    <!-- Top bar -->
    <template #topBarRight>
      <div class="action-panel">
        <!-- Grouping -->
        <b-dropdown right no-caret toggle-class="action-btn icon-btn">
          <template #button-content>
            <i class="fas fa-chart-bar"></i>
          </template>
          <b-dropdown-text class="small text-secondary">GROUP BY</b-dropdown-text>
          <b-dropdown-item
            v-for="grouping in groupingOptions"
            :key="grouping.key"
            @click.native.capture.stop.prevent="() => updateChartGrouping(grouping)"
          >
            <i
              class="fas fa-check text-primary"
              :style="{ visibility: activeGrouping === grouping.key ? 'visible' : 'hidden' }"
            ></i>
            <span>{{ grouping.title }}</span>
          </b-dropdown-item>
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
                key: 'grouping',
                icon: 'fas fa-chart-bar',
                title: `Group By`,
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
            <template #grouping>
              <b-dropdown-text class="small text-secondary">GROUP BY</b-dropdown-text>
              <b-dropdown-item
                v-for="grouping in groupingOptions"
                :key="grouping.key"
                @click.native.capture.stop.prevent="() => updateChartGrouping(grouping)"
              >
                <i
                  class="fas fa-check text-primary"
                  :style="{ visibility: activeGrouping === grouping.key ? 'visible' : 'hidden' }"
                ></i>
                <span>{{ grouping.title }}</span>
              </b-dropdown-item>
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

      <loading-placeholder v-if="!stats" />
      <b-container v-else>
        <b-row>
          <b-col>
            <muted-alert>Statistics also include deleted prints</muted-alert>
          </b-col>
        </b-row>
        <b-row>
          <b-col>
            <h2 class="section-title">General</h2>
          </b-col>
        </b-row>
        <b-row>
          <b-col lg="6" class="mb-4 mb-lg-0">
            <div class="stats-block">
              <div class="stats-block-title">
                <i class="fas fa-hashtag"></i>
                <span>Total prints</span>
              </div>
              <!-- TODO: donut chart -->
            </div>
          </b-col>
          <b-col lg="6">
            <div class="stats-block print-time">
              <div class="stats-block-title">
                <i class="far fa-clock"></i>
                <span>Print time</span>
              </div>
              <div class="info total-print-time">
                <div class="title">Total print time</div>
                <div class="value">{{ stats.total_print_time | durationLong }}</div>
              </div>
              <div class="other-print-time-numbers">
                <div class="info">
                  <div class="title">Longest print</div>
                  <div class="value">{{ stats.longest_print_time | durationShort }}</div>
                </div>
                <div class="divider"></div>
                <div class="info">
                  <div class="title">Average print</div>
                  <div class="value">{{ stats.average_print_time | durationShort }}</div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>

      <!-- Date picker for filter by time period -->
      <date-picker-modal ref="datePickerModal" @picked="onDatesPicked" />
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@config/server-urls'
import PageLayout from '@src/components/PageLayout.vue'
import { user } from '@src/lib/page-context'
import MutedAlert from '../components/MutedAlert.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import FilteringDropdown, { restoreFilterValues } from '@src/components/FilteringDropdown'
import ActiveFilterNotice from '@src/components/ActiveFilterNotice'
import DatePickerModal from '@src/components/DatePickerModal.vue'
import { getLocalPref, setLocalPref } from '@src/lib/pref'

const DateParamFormat = 'YYYY-MM-DD'
const FilterLocalStoragePrefix = 'statsFiltering'
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
  name: 'StatsPage',

  components: {
    PageLayout,
    MutedAlert,
    CascadedDropdown,
    FilteringDropdown,
    ActiveFilterNotice,
    DatePickerModal,
  },

  filters: {
    durationLong(v) {
      const duration = moment.duration(v, 'seconds')
      const days = duration.days()
      const daysText = days ? `${days} day${days !== 1 ? 's ' : ' '}` : ''
      const hours = duration.hours()
      const hoursText = `${hours} hour${hours !== 1 ? 's ' : ' '}`
      const minutes = duration.minutes()
      const minutesText = `${minutes} minute${minutes !== 1 ? 's' : ''}`
      return `${daysText}${hoursText}${minutesText}`
    },
    durationShort(v) {
      const duration = moment.duration(v, 'seconds')
      const days = duration.days()
      const daysText = days ? `${days}d ` : ''
      const hours = duration.hours()
      const hoursText = `${hours}h `
      const minutes = duration.minutes()
      const minutesText = `${minutes}m`
      return `${daysText}${hoursText}${minutesText}`
    },
  },

  data: function () {
    return {
      user: null,
      stats: null,

      groupingOptions: [
        { key: 'day', title: 'Day' },
        { key: 'week', title: 'Week' },
        { key: 'month', title: 'Month' },
        { key: 'year', title: 'Year' },
      ],
      activeGrouping: 'day',

      // Filtering
      filterLocalStoragePrefix: FilterLocalStoragePrefix,
      filterOptions: FilterOptions,
      filterValues: restoreFilterValues(FilterLocalStoragePrefix, FilterOptions),
    }
  },

  computed: {
    defaultStatsParams() {
      return {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        from_date: moment(this.user.date_joined).format(DateParamFormat),
        to_date: moment(new Date()).format(DateParamFormat),
        group_by: this.activeGrouping,
      }
    },
  },

  created() {
    this.user = user()

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

        this.fetchStats()
      })
  },

  mounted() {},

  methods: {
    fetchStats() {
      axios
        .get(urls.stats(), {
          params: {
            ...this.defaultStatsParams,
          },
        })
        .then((response) => {
          console.log(response)
          this.stats = response.data
        })
        .catch((error) => {
          this._showErrorPopup(error)
        })
    },
    updateChartGrouping(grouping) {
      this.activeGrouping = grouping.key
      this.fetchStats()
    },

    // Filtering
    onFilterUpdated(filterOptionKey, filterOptionValue) {
      this.filterValues[filterOptionKey] = filterOptionValue
      this.fetchStats()
    },
    resetFilters() {
      for (const key of Object.keys(this.filterValues)) {
        this.filterValues[key] = 'none'
        setLocalPref(`${FilterLocalStoragePrefix}-${key}`, 'none')
      }
      this.updateCustomPeriodFilterSubtitle()
      this.fetchStats()
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
      this.fetchStats()
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
.stats-block
  background-color: var(--color-surface-secondary)
  padding: 1.75em 2.25em
  border-radius: var(--border-radius-lg)
  height: 280px

.stats-block-title
  font-size: 1.125rem
  color: var(--color-text-primary)
  font-weight: medium
  span
    display: inline-block
    margin-left: .5em
  i
    color: var(--color-divider)

.print-time
  display: flex
  flex-direction: column
  justify-content: space-between
  .title
    font-size: 1.125rem
    color: var(--color-text-secondary)
  .value
    font-size: 1.5rem
    color: var(--color-text-primary)
  .other-print-time-numbers
    display: flex
    .divider
      width: 1px
      background-color: var(--color-divider)
      margin: 0 2rem
    .info
      .title
        font-size: .875rem
      .value
        font-size: 1.125rem
</style>
