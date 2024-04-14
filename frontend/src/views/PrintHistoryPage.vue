<template>
  <page-layout>
    <!-- Top bar -->
    <template #topBarLeft>
      <div class="actions-with-selected-desktop">
        <b-form-group class="m-0">
          <b-form-checkbox v-model="allPrintsSelected" size="md"></b-form-checkbox>
        </b-form-group>
        <div>
          <span
            v-show="!selectedPrintIds.size"
            class="label"
            @click="allPrintsSelected = !allPrintsSelected"
            >{{ $t("Select all") }}</span
          >
          <b-dropdown
            v-show="selectedPrintIds.size"
            toggle-class="btn btn-sm actions-with-selected-btn"
          >
            <template #button-content>
              {{ selectedPrintIds.size }} item{{ selectedPrintIds.size === 1 ? '' : 's' }}
              {{$t("selected")}}
            </template>
            <b-dropdown-item>
              <div class="text-danger" @click="onDeleteBtnClick">
                <i class="far fa-trash-alt"></i>{{$t("Delete")}}
              </div>
            </b-dropdown-item>
          </b-dropdown>
        </div>
      </div>
    </template>
    <template #topBarRight>
      <div class="action-panel">
        <!-- Sorting -->
        <b-dropdown right no-caret toggle-class="action-btn icon-btn" :title="$t('Sort By')">
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
                key: 'sorting',
                icon: 'fas fa-sort-amount-down',
                title: $t(`Sort`),
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
                  <div class="title">{{ $t("Prints done") }}</div>
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
                  <div class="title">{{ $t("Total print time") }}</div>
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
                      {{$t("Filament used")}}
                    </help-widget>
                  </div>
                  <div class="value">{{ totalFilamentUsedFormatted }}</div>
                </div>
              </div>
              <div class="btn-wrapper">
                <a class="btn btn-secondary" :href="`/stats/`">
                  {{$t("Full Stats")}}
                  <i class="fas fa-arrow-right"></i>
                </a>
              </div>
            </div>
          </b-col>
        </b-row>
        <b-row>
          <b-col v-if="prints.length || loading">
            <print-history-item
              v-for="(print, index) of prints"
              :key="print.id"
              :print="print"
              :index="index"
              :selectable="true"
              :selected="selectedPrintIds.has(print.id)"
              class="print-item"
              @selectedChanged="onSelectedChanged"
            ></print-history-item>
            <mugen-scroll :handler="fetchMoreData" :should-handle="!loading">
              <loading-placeholder v-if="!noMoreData" />
            </mugen-scroll>
          </b-col>
          <b-col v-else class="text-center my-5">{{ $t("No prints found") }}</b-col>
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
import { queryBuilder } from '@src/lib/time-period-filtering'
import { humanizedFilamentUsage, humanizedDuration } from '@src/lib/formatters'
import i18n from '@src/i18n/i18n.js'
const PAGE_SIZE = 24

export const SortingLocalStoragePrefix = 'printsSorting'
export const SortingOptions = {
  options: [{ title: `${i18n.t('Date')}`, key: 'date' }],
  default: { sorting: 'date', direction: 'desc' },
}

const DateParamFormat = 'YYYY-MM-DD'
export const FilterLocalStoragePrefix = 'printsFiltering'
export const FilterOptions = {
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
  feedbackNeeded: {
    title: `${i18n.t('Feedback Needed')}`,
    queryParam: 'feedback_needed',
    values: [
      { key: 'none', title: `${i18n.t('All' )}`},
      { key: 'need_alert_overwrite', title: `${i18n.t('Review Needed' )}`},
      { key: 'need_print_shot_feedback', title: `${i18n.t('Focused Feedback Needed' )}`},
    ],
    default: 'none',
  },
  printers: {
    title: `${i18n.t('Printers')}`,
    queryParam: 'filter_by_printer_ids',
    multiple: true,
    values: [
      { key: 'none', title:`${i18n.t('All')}`, includesAll: true },
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
      selectedPrintIds: new Set(),

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
      return humanizedDuration(this.stats.total_print_time)
    },
    totalFilamentUsedFormatted() {
      return humanizedFilamentUsage(this.stats?.total_filament_used)
    },
    defaultStatsParams() {
      return {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        from_date: moment(this.user.date_joined).format(DateParamFormat),
        to_date: moment(new Date()).format(DateParamFormat),
        group_by: 'year',
      }
    },
    allPrintsSelected: {
      get: function () {
        return this.selectedPrintIds.size >= this.prints.length && this.prints.length !== 0
      },
      set: function (newValue) {
        if (newValue) {
          this.selectedPrintIds = new Set(this.prints.map((p) => p.id))
        } else {
          if (this.selectedPrintIds.size === this.prints.length) {
            this.selectedPrintIds = new Set()
          }
        }
      },
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
          this.errorDialog(error)
        })
    },
    refetchData() {
      this.prints = []
      this.selectedPrintIds = new Set()
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
          this.errorDialog(error)
        })
    },

    onSelectedChanged(printId, selected) {
      const selectedPrintIdsClone = new Set(this.selectedPrintIds)
      if (selected) {
        selectedPrintIdsClone.add(printId)
      } else {
        selectedPrintIdsClone.delete(printId)
      }
      this.selectedPrintIds = selectedPrintIdsClone
    },
    onDeleteBtnClick() {
      const selectedPrintIds = Array.from(this.selectedPrintIds)
      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Are you sure?')}`,
        text: `${this.$i18next.t(`Delete {name} print(s)? This action can not be undone.`,{name:this.selectedPrintIds.size})}`,
        showCancelButton: true,
        confirmButtonText: `${this.$i18next.t('Yes')}`,
        cancelButtonText: `${this.$i18next.t('No')}`,
      }).then((userAction) => {
        if (userAction.isConfirmed) {
          axios.post(urls.printsBulkDelete(), { print_ids: selectedPrintIds }).then(() => {
            this.refetchData()
          })
        }
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
          : `${this.$i18next.t('Until')}`
        const dateToFormatted = currentDateTo
          ? moment(currentDateTo).format(dateFormat)
          : `${this.$i18next.t('and later')}`

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
  justify-content: space-between
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

.actions-with-selected-desktop
  display: flex
  align-items: center
  .label
    cursor: pointer
  ::v-deep .custom-checkbox .custom-control-label::before
    border-radius: var(--border-radius-xs)
</style>
