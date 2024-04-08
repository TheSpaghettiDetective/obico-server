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
          <b-dropdown-text class="small text-secondary">{{ $t("GROUP BY") }}</b-dropdown-text>
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
          :title="$t('Filter')"
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
                title: $t(`Group By`),
                expandable: true,
              },
              {
                key: 'filtering',
                icon: 'fas fa-filter',
                title: $t(`Filter`),
                expandable: true,
              },
            ]"
          >
            <template #grouping>
              <b-dropdown-text class="small text-secondary">{{ $t("GROUP BY") }}</b-dropdown-text>
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
            <muted-alert class="muted-alert">{{ $t("Statistics include deleted prints") }}</muted-alert>
          </b-col>
        </b-row>
        <b-row>
          <b-col lg="6" class="mb-4 mb-lg-0">
            <div class="stats-block total-prints">
              <div class="stats-block-title">
                <i class="fas fa-hashtag"></i>
                <span>{{ $t("Total Prints") }}</span>
              </div>
              <div class="chart-wrapper">
                <div class="legend">
                  <div class="line">
                    <div class="square success"></div>
                    <div class="title">{{ $t("Finished") }}:</div>
                    <div class="value">{{ stats ? stats.total_succeeded_print_count : '' }}</div>
                  </div>
                  <div class="line">
                    <div class="square danger"></div>
                    <div class="title">{{ $t("Cancelled") }}:</div>
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
                <span>{{ $t("Print Time") }}</span>
              </div>
              <div class="info total-print-time">
                <div class="title">{{ $t("Total print time") }}</div>
                <div class="value">{{ humanizedDuration(stats.total_print_time) }}</div>
              </div>
              <div class="other-print-time-numbers">
                <div class="info">
                  <div class="title">{{ $t("Longest print") }}</div>
                  <div class="value">{{ humanizedDuration(stats.longest_print_time) }}</div>
                </div>
                <div class="divider"></div>
                <div class="info">
                  <div class="title">{{ $t("Average print") }}</div>
                  <div class="value">{{ humanizedDuration(stats.average_print_time) }}</div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
        <b-row class="mt-4">
          <b-col>
            <div class="stats-block bar-chart">
              <div class="stats-block-title">
                <i class="fas fa-hashtag"></i>
                <span>{{ $t("Prints Count") }}</span>
              </div>
              <div ref="printCountGroupsChart" class="bar-chart-wrapper"></div>
            </div>
          </b-col>
        </b-row>
        <b-row class="mt-4">
          <b-col>
            <div class="stats-block bar-chart">
              <div class="stats-block-title">
                <i class="far fa-clock"></i>
                <span>{{ $t("Print Time") }}</span>
              </div>
              <div ref="printTimeGroupsChart" class="bar-chart-wrapper"></div>
            </div>
          </b-col>
        </b-row>
        <b-row class="mt-4">
          <b-col>
            <div class="stats-block bar-chart filament-used-groups">
              <div class="stats-block-title">
                <i class="fas fa-ruler-horizontal"></i>
                <div class="title-group">
                  <span>
                    <help-widget
                      id="filament-used-may-be-incorrect"
                      :highlight="false"
                      :show-close-button="false"
                    >
                      {{$t("Filament Usage")}}
                    </help-widget>
                  </span>
                  <div class="divider"></div>
                  <div class="subtitle">{{ totalFilamentUsedFormatted }} {{$t("total")}}</div>
                </div>
              </div>
              <div ref="filamentUsedGroupsChart" class="bar-chart-wrapper"></div>
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
import { queryBuilder, getDateTo, getRecommendedGrouping } from '@src/lib/time-period-filtering'
import HelpWidget from '@src/components/HelpWidget.vue'
import { humanizedDuration, humanizedFilamentUsage } from '@src/lib/formatters'
import i18n from "@src/i18n/i18n.js"
const GroupingLocalStorageKey = 'statsGrouping'

const DateParamFormat = 'YYYY-MM-DD'
const FilterLocalStoragePrefix = 'statsFiltering'
const FilterOptions = {
  timePeriod: {
    title: `${i18n.t('Time Period')}`,
    buildQueryParam: queryBuilder,
    values: [
      { key: 'none', title: `${i18n.t('All') }`},
      { key: 'this_week', title: `${i18n.t('This Week') }`},
      { key: 'this_month', title: `${i18n.t('This Month') }`},
      { key: 'this_year', title: `${i18n.t('This Year') }`},
      { key: 'custom', title: `${i18n.t('Custom') }`},
    ],
    default: 'none',
  },
  printStatus: {
    title: `${i18n.t('Print Status')}`,
    queryParam: 'filter',
    values: [
      { key: 'none', title: `${i18n.t('All') }`},
      { key: 'finished', title: `${i18n.t('Finished') }`},
      { key: 'cancelled', title: `${i18n.t('Cancelled') }`},
    ],
    default: 'none',
  },
  printers: {
    title: `${i18n.t('Printers')}`,
    queryParam: 'filter_by_printer_ids',
    multiple: true,
    values: [
      { key: 'none', title: `${i18n.t('All')}`, includesAll: true },
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
    HelpWidget,
  },

  data: function () {
    return {
      user: null,
      stats: null,

      groupingOptions: [
        { key: 'auto', title: 'Auto' },
        { key: 'day', title: 'Day' },
        { key: 'week', title: 'Week' },
        { key: 'month', title: 'Month' },
        { key: 'year', title: 'Year' },
      ],
      activeGrouping: getLocalPref(GroupingLocalStorageKey, 'auto'),

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
        group_by: this.getActiveGrouping(),
      }
    },

    isEmptyState() {
      return !this.stats?.total_print_count
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

    totalFilamentUsedFormatted() {
      return humanizedFilamentUsage(this.stats?.total_filament_used)
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
    getFilterParamsFromQuery() {
      let params = {}
      const urlParams = new URLSearchParams(window.location.search)
      const entries = urlParams.entries()

      // frontend params without need to be passed to backend
      const excludeParams = ['hide_header']

      for (const [key, value] of entries) {
        if (key && value && !excludeParams.includes(key)) {
          params[key] = params[key]
            ? Array.isArray(params[key])
              ? [...params[key], value]
              : [params[key], value]
            : value
        }
      }
      console.log('params', params)
      return params
    },
    fetchStats() {
      axios
        .get(urls.stats(), {
          params: {
            with_deleted: true,
            ...this.defaultStatsParams,
            ...getFilterParams(
              this.filterOptions,
              this.filterValues,
              this.customFilterParamsBuilder
            ),
            ...this.getFilterParamsFromQuery(),
          },
        })
        .then((response) => {
          this.stats = response.data
          this.$nextTick(this.drawCharts)
        })
        .catch((error) => {
          this.errorDialog(error, `${this.$i18next.t('Failed to fetch statistics')}`)
        })
    },
    updateChartGrouping(grouping) {
      this.activeGrouping = grouping.key
      setLocalPref(GroupingLocalStorageKey, grouping.key)
      this.fetchStats()
    },
    drawCharts() {
      if (!this.stats) {
        return
      }

      this.$refs.totalPrintsDonutChart.replaceChildren(
        DonutChart(
          [
            {
              name: 'Finished',
              value: this.isEmptyState ? 0.5 : this.finishedPrintsPercentage / 100,
            },
            {
              name: 'Cancelled',
              value: this.isEmptyState ? 0.5 : this.cancelledPrintsPercentage / 100,
            },
          ],
          {
            name: (d) => d.name,
            value: (d) => d.value,
            format: '.0%',
            totalValue: this.isEmptyState
              ? '0'
              : this.stats.total_succeeded_print_count + this.stats.total_cancelled_print_count,
            names: ['Finished', 'Cancelled'],
            colors: ['var(--color-success)', 'var(--color-danger)'],
            emptyState: this.isEmptyState,
          }
        )
      )

      // Print count groups bars
      const printCountMaxValue = Math.max(...this.stats.print_count_groups.map((d) => d.value))
      this.drawBarChart({
        data: this.stats.print_count_groups,
        ref: this.$refs.printCountGroupsChart,
        yFormat: 'd',
        titleValue: (v) => `${v} print(s)`,
        yDomain: [0, printCountMaxValue || 1],
        yTicks: Math.min(printCountMaxValue || 1, 5),
      })

      // Print time groups bars
      const printTimeMaxValue = Math.max(...this.stats.print_time_groups.map((d) => d.value))
      const printTimeMaxvalueHours = Math.round(printTimeMaxValue / 3600)
      this.drawBarChart({
        data: this.stats.print_time_groups.map((d) => ({ ...d, value: d.value / 3600 })),
        ref: this.$refs.printTimeGroupsChart,
        yFormat: 'd',
        yTickFormat: (h) => {
          if (h > 24 * 365) {
            return `${Math.round(h / (24 * 365))}y`
          } else if (h >= 24) {
            return `${Math.round(h / 24)}d`
          } else {
            return `${h}h`
          }
        },
        titleValue: (v) => this.humanizedDuration(v * 3600),
        yDomain: [0, printTimeMaxvalueHours || 1],
        yTicks: Math.min(printTimeMaxvalueHours || 1, 5),
      })

      // Filament used groups bars
      const filamentUsedMaxValue = Math.max(...this.stats.filament_used_groups.map((d) => d.value))
      const filamentUsedMaxvalueMeters = Math.round(filamentUsedMaxValue / 1000)
      this.drawBarChart({
        data: this.stats.filament_used_groups.map((d) => ({ ...d, value: d.value / 1000 })),
        ref: this.$refs.filamentUsedGroupsChart,
        yFormat: 'd',
        yTickFormat: (m) => `${m}m`,
        titleValue: (v) => (v >= 1000 ? Math.round(v / 1000) + 'km' : v + 'm'),
        yDomain: [0, filamentUsedMaxvalueMeters || 1],
        yTicks: Math.min(filamentUsedMaxvalueMeters || 1, 5),
      })
    },
    drawBarChart({ data, ref, yFormat, yTickFormat, yTicks, yDomain, titleValue }) {
      const chartWidth = ref.offsetWidth
      const barsCount = data.length
      const xLabelsFormat = xAxisLabelsFormat(
        chartWidth,
        barsCount,
        this.getFilterParamsFromQuery()?.group_by || this.getActiveGrouping(),
        getDateTo(this.filterValues.timePeriod, this.getCurrentDateTo())
      )

      ref.replaceChildren(
        BarChart(data, {
          xLabelRotation: xLabelsFormat.rotation,
          xLabelShow: xLabelsFormat.shouldShow,
          x: xLabelsFormat.value,
          y: (d) => d.value,
          yFormat,
          yTickFormat,
          yDomain,
          yTicks,
          width: chartWidth,
          color: 'var(--color-divider)',
          title: (d) => {
            const label = xLabelsFormat.value(d).split('\r')[0].split('\n')
            return `${label[0] + (label[1] ? ', ' + label[1] : '')} — ${
              titleValue ? titleValue(d.value) : d.value
            }`
          },
          marginBottom: 55,
        })
      )
    },

    humanizedDuration,

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
    // time periods grouping
    getActiveGrouping() {
      return this.activeGrouping === 'auto'
        ? getRecommendedGrouping(
            this.filterValues.timePeriod,
            this.getCurrentDateFrom(),
            this.getCurrentDateTo(),
            this.user
          )
        : this.activeGrouping
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
.muted-alert
  margin-bottom: var(--gap-between-blocks)

.stats-block
  background-color: var(--color-surface-secondary)
  padding: 1.75em 2.25em
  border-radius: var(--border-radius-lg)
  height: 280px
  display: flex
  flex-direction: column
  &.bar-chart
    height: auto
    .chart-wrapper
      height: 210px
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

.filament-used-groups
  .title-group
    display: inline-flex
    align-items: center
    gap: .875rem
    @media (max-width: 768px)
      margin-left: 0.5rem
      flex-direction: column
      align-items: flex-start
      gap: 0
      .divider
        display: none
      span
        margin-left: 0
    .divider
      width: 1px
      background-color: var(--color-divider)
      height: 1.25rem
</style>
