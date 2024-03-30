<template>
  <page-layout>
    <template #topBarLeft>
      <div class="actions-with-selected-desktop">
        <b-form-group class="m-0">
          <b-form-checkbox v-model="allPrintsSelected" size="lg"></b-form-checkbox>
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
            class=""
            toggle-class="btn btn-sm actions-with-selected-btn"
          >
            <template #button-content>
              {{ selectedPrintIds.size }} item{{ selectedPrintIds.size === 1 ? '' : 's' }}
              {{$t("selected...")}}
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
            :local-storage-prefix="filterLocalStoragePrefix"
            :filter-options="filterOptions"
            :filter-values="filterValues"
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
                :local-storage-prefix="filterLocalStoragePrefix"
                :filter-options="filterOptions"
                :filter-values="filterValues"
                @onFilterUpdated="onFilterUpdated"
              />
            </template>
          </cascaded-dropdown>
        </b-dropdown>
      </div>
    </template>
    <template #content>
      <active-filter-notice :filter-values="filterValues" @onShowAllClicked="resetFilters" />

      <b-container>
        <b-row v-show="prints.length" class="print-cards">
          <print-card
            v-for="print of visiblePrints"
            :key="print.id"
            :print="print"
            :selected="selectedPrintIds.has(print.id)"
            @selectedChanged="onSelectedChanged"
            @printDeleted="onPrintDeleted"
            @printDataChanged="printDataChanged"
            @fullscreen="openFullScreen"
          ></print-card>
        </b-row>

        <mugen-scroll :handler="fetchMoreData" :should-handle="!loading" class="text-center p-4">
          <div v-if="noMoreData" class="text-center p-2">{{ $t("No more time-lapses.") }}</div>
          <b-spinner v-if="!noMoreData" :label="$t('Loading...')"></b-spinner>
        </mugen-scroll>

        <b-modal
          id="tl-fullscreen-modal"
          size="full"
          :hide-header="true"
          :hide-footer="true"
          @hidden="fullScreenClosed"
        >
          <FullScreenPrintCard
            :print="fullScreenPrint"
            :video-url="fullScreenPrintVideoUrl"
            :autoplay="true"
          />
        </b-modal>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import findIndex from 'lodash/findIndex'
import MugenScroll from 'vue-mugen-scroll'
import map from 'lodash/map'
import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import { setLocalPref } from '@src/lib/pref'
import PrintCard from '@src/components/prints/PrintCard.vue'
import FullScreenPrintCard from '@src/components/prints/FullScreenPrintCard.vue'
import PageLayout from '@src/components/PageLayout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import ActiveFilterNotice from '@src/components/ActiveFilterNotice'
import SortingDropdown, { restoreSortingValue } from '@src/components/SortingDropdown'
import FilteringDropdown, {
  restoreFilterValues,
  getFilterParams,
} from '@src/components/FilteringDropdown'
import i18n from '@src/i18n/i18n.js'

const PAGE_SIZE = 6

const SortingLocalStoragePrefix = 'printsPageSorting'
const SortingOptions = {
  options: [{ title: `${i18n.t('Date')}`, key: 'date' }],
  default: { sorting: 'date', direction: 'desc' },
}

const FilterLocalStoragePrefix = 'printsPageFiltering'
const FilterOptions = {
  printStatus: {
    title: `${i18n.t('Print Status')}`,
    queryParam: 'filter',
    values: [
      { key: 'none', title: `${i18n.t('All')}` },
      { key: 'finished', title: `${i18n.t('Finished')}` },
      { key: 'cancelled', title: `${i18n.t('Cancelled')}` },
    ],
    default: 'none',
  },
  feedbackNeeded: {
    title: `${i18n.t('Feedback Needed')}`,
    queryParam: 'feedback_needed',
    values: [
      { key: 'none', title: `${i18n.t('All')}` },
      { key: 'need_alert_overwrite', title: `${i18n.t('Review Needed')}` },
      { key: 'need_print_shot_feedback', title: `${i18n.t('Focused Feedback Needed')}` },
    ],
    default: 'none',
  },
}

export default {
  name: 'PrintsPage',

  components: {
    MugenScroll,
    PrintCard,
    FullScreenPrintCard,
    PageLayout,
    CascadedDropdown,
    FilteringDropdown,
    SortingDropdown,
    ActiveFilterNotice,
  },

  data: function () {
    return {
      prints: [],
      selectedPrintIds: new Set(),
      loading: false,
      noMoreData: false,
      fullScreenPrint: null,
      fullScreenPrintVideoUrl: null,

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
    visiblePrints() {
      return this.prints.filter((p) => p.ended_at)
    },
    allPrintsSelected: {
      get: function () {
        return this.selectedPrintIds.size >= this.prints.length && this.prints.length !== 0
      },
      set: function (selected) {
        if (selected) {
          this.selectedPrintIds = new Set(map(this.prints, 'id'))
        } else {
          this.selectedPrintIds = new Set()
        }
      },
    },
  },

  created() {
    this.refetchData()
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
    },
    refetchData() {
      this.prints = []
      this.selectedPrintIds = new Set()
      this.noMoreData = false
      this.fetchMoreData()
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
        text: `${this.$i18next.t(`Delete {brandName} print(s)? This action can not be undone.`,{brandName:this.$syndicateText.brandName})}`,
        showCancelButton: true,
        confirmButtonText: `${this.$i18next.t('Yes')}`,
        cancelButtonText: `${this.$i18next.t('No')}`,
      }).then((userAction) => {
        if (userAction.isConfirmed) {
          axios.post(urls.printsBulkDelete(), { print_ids: selectedPrintIds }).then(() => {
            selectedPrintIds.forEach((printId) => this.onPrintDeleted(printId, false))
            this.$swal.Toast.fire({
              title: `${this.$i18next.t(`{name} time-lapse(s) deleted!`,{name:selectedPrintIds.length})}`,
            })
            this.selectedPrintIds = new Set()
          })
        }
      })
    },
    onPrintDeleted(printId, toast = true) {
      const i = findIndex(this.prints, (p) => p.id == printId)
      const print = this.prints[i]
      this.$delete(this.prints, i)
      if (toast) {
        this.$swal.Toast.fire({
          title: `${this.$i18next.t(`Time-lapse {name} deleted!`,{name:print.filename})}`,
        })
      }
    },
    printDataChanged(data) {
      const i = findIndex(this.prints, (p) => p.id == data.id)
      this.$set(this.prints, i, normalizedPrint(data))
    },
    openFullScreen(printId, videoUrl) {
      const i = findIndex(this.prints, (p) => p.id == printId)
      if (i != -1) {
        this.fullScreenPrint = this.prints[i]
        this.fullScreenPrintVideoUrl = videoUrl
        this.$bvModal.show('tl-fullscreen-modal')
      }
    },
    fullScreenClosed() {
      this.fullScreenPrint = null
      this.fullScreenPrintVideoUrl = null
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
      this.refetchData()
    },
  },
}
</script>

<style lang="sass" scoped>
.print-cards
  margin-top: calc(var(--gap-between-blocks) * -1)
.menu-bar
  background-color: var(--color-surface-secondary)
  padding: 0.75rem 1.25rem
#tl-fullscreen-modal
  .modal-full
    max-width: 100%
  .modal-body
    padding: 0
  .video-js
    height: calc(100vh - 200px)
::v-deep .btn-outline-secondary
  color: var(--color-text-primary)
  border-color: var(--color-text-primary)
  &:hover
    background: none
    opacity: .8
.actions-with-selected-desktop
  display: flex
  align-items: center
  .label
    cursor: pointer
  ::v-deep .actions-with-selected-btn
    border-radius: 0
</style>
