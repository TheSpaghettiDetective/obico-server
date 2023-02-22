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
            <muted-alert>Statistics numbers include deleted prints</muted-alert>
          </b-col>
        </b-row>
        <!-- <b-row>
          <b-col>
            <h2 class="section-title">General</h2>
          </b-col>
        </b-row> -->
        <b-row>
          <b-col lg="6" class="mb-4 mb-lg-0">
            <div class="stats-block total-prints">
              <div class="stats-block-title">
                <i class="fas fa-hashtag"></i>
                <span>Total prints</span>
              </div>
              <div class="chart-wrapper">
                <div class="legend">
                  <div class="line">
                    <div class="square success"></div>
                    <div class="title">Finished:</div>
                    <div class="value">{{ stats ? stats.total_succeeded_print_count : '' }}</div>
                  </div>
                  <div class="line">
                    <div class="square danger"></div>
                    <div class="title">Cancelled:</div>
                    <div class="value">{{ stats ? stats.total_cancelled_print_count : '' }}</div>
                  </div>
                </div>
                <div ref="totalPrintsDonutChart"></div>
              </div>
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
        <b-row class="mt-4">
          <b-col>
            <div class="stats-block print-count-groups">
              <div class="stats-block-title">
                <i class="fas fa-hashtag"></i>
                <span>Prints</span>
              </div>
              <div ref="printCountGroupsChart"></div>
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
import FilteringDropdown, {
  restoreFilterValues,
  getFilterParams,
} from '@src/components/FilteringDropdown'
import ActiveFilterNotice from '@src/components/ActiveFilterNotice'
import DatePickerModal from '@src/components/DatePickerModal.vue'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import { DonutChart } from '@src/lib/charts/donut-chart'
import { BarChart, xAxisLabelsFormat } from '@src/lib/charts/bar-chart'
import timePeriodFilteringQueryBuilder from '@src/lib/time-period-filtering-query-builder'

const DateParamFormat = 'YYYY-MM-DD'
const FilterLocalStoragePrefix = 'statsFiltering'
const FilterOptions = {
  timePeriod: {
    title: 'Time Period',
    buildQueryParam: timePeriodFilteringQueryBuilder,
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

    // Total prints count
    finishedPrintsPercentage() {
      const finished = this.stats?.total_succeeded_print_count
      const total = this.stats?.total_print_count

      if (!finished || !total) {
        return 0
      }

      return Math.round((finished / total) * 100)
    },
    cancelledPrintsPercentage() {
      const total = this.stats?.total_print_count

      if (!total) {
        return 0
      } else {
        return 100 - this.finishedPrintsPercentage
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

        this.fetchStats()
      })
  },

  mounted() {
    addEventListener('resize', this.drawCharts)
  },

  unmounted() {
    removeEventListener('resize', this.drawCharts)
  },

  methods: {
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
          this.$nextTick(this.drawCharts)
        })
        .catch((error) => {
          this._showErrorPopup(error)
        })
    },
    updateChartGrouping(grouping) {
      this.activeGrouping = grouping.key
      this.fetchStats()
    },
    drawCharts() {
      if (!this.stats) {
        return
      }

      this.$refs.totalPrintsDonutChart.replaceChildren(
        DonutChart(
          [
            { name: 'Finished', value: this.finishedPrintsPercentage / 100 },
            { name: 'Cancelled', value: this.cancelledPrintsPercentage / 100 },
          ],
          {
            name: (d) => d.name,
            value: (d) => d.value,
            format: '.0%',
            totalValue:
              this.stats.total_succeeded_print_count + this.stats.total_cancelled_print_count,
            names: ['Finished', 'Cancelled'],
            colors: ['var(--color-success)', 'var(--color-danger)'],
          }
        )
      )

      // Print count groups bars
      const chartWidth = this.$refs.printCountGroupsChart.offsetWidth
      const barsCount = this.stats.print_count_groups.length
      const xLabelsFormat = xAxisLabelsFormat(chartWidth, barsCount)
      const maxValue = Math.max(...this.stats.print_count_groups.map((d) => d.value))
      this.$refs.printCountGroupsChart.replaceChildren(
        BarChart(this.stats.print_count_groups, {
          xLabelRotation: xLabelsFormat.rotation,
          xLabelShow: xLabelsFormat.shouldShow,
          x: xLabelsFormat.value,
          y: (d) => d.value,
          yFormat: 'd', // decimal
          yDomain: [0, maxValue || 1],
          yTicks: Math.min(maxValue || 1, 5),
          width: chartWidth,
          color: 'var(--color-divider)',
          title: (d) => `${moment(d.key).format('MMM D, YYYY')} — ${d.value} print(s)`,
        })
      )
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
  display: flex
  flex-direction: column
  @media (max-width: 768px)
    padding: 1.25em 1.5em

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

.total-prints
  .chart-wrapper
    flex: 1
    display: flex
    justify-content: space-between
    align-items: center
    gap: 1rem
  .legend
    display: flex
    flex-direction: column
    justify-content: center
  .line
    display: flex
    align-items: center
    gap: .3rem
    margin: .25rem 0
    @media (max-width: 768px)
      font-size: .875rem
  .square
    width: 1.125rem
    height: 1.125rem
    border-radius: var(--border-radius-xs)
    margin-right: .2rem
    &.success
      background-color: var(--color-success)
    &.danger
      background-color: var(--color-danger)
  .value
    font-weight: bold
</style>
