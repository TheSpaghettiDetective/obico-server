<template>
  <page-layout>
    <template #topBarRight>
      <div class="action-panel">
        <!-- Detection Hours -->
        <a
          v-if="isEnt"
          href="/user_preferences/dh/"
          class="btn shadow-none action-btn icon-btn hours-btn"
          :style="{ marginRight: `${String(dhBadgeNum).length * 0.25}rem` }"
          :title="dhBadgeNum + ' ' + $t('AI Detection Hours')"
        >
          <svg class="custom-svg-icon">
            <use href="#svg-hour-glass"></use>
          </svg>
          <span id="user-credits" class="badge badge-light">{{ dhBadgeNum }}</span>
          <span class="sr-only">{{ $t("AI Detection Hours") }}</span>
        </a>
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
          <cascaded-dropdown ref="cascadedDropdown" :menu-options="mobileMenuOptions">
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

    <!-- Page content -->
    <template #content>
      <active-filter-notice :filter-values="filterValues" @onShowAllClicked="resetFilters" />

      <!-- Printers list -->
      <b-container class="printer-list-page">
        <b-row v-if="loading">
          <b-col class="text-center">
            <b-spinner class="my-5" label="Loading..."></b-spinner>
          </b-col>
        </b-row>
        <b-row v-if="visiblePrinters.length" class="printer-cards justify-content-center">
          <printer-card
            v-for="printer in visiblePrinters"
            :key="printer.id"
            :printer="printer"
            :is-pro-account="user.is_pro"
            class="printer-card-wrapper"
            @PrinterUpdated="onPrinterUpdated"
          ></printer-card>
        </b-row>
        <div v-if="!loading" class="row justify-content-center">
          <div id="new-printer" class="col-sm-12 col-lg-6">
            <div class="new-printer-container">
              <a href="/printers/wizard/">
                <svg class="icon">
                  <use href="#svg-add-printer"></use>
                </svg>
                <div>{{ $t("Link New Printer") }}</div>
              </a>
            </div>
          </div>
        </div>
        <b-row v-if="!loading" v-show="shouldShowArchiveWarning" class="bottom-messages">
          <b-col>
            <div class="alert alert-warning alert-dismissible fade show mb-3" role="alert">
              <div class="warning">
                <div>
                  {{ archivedPrinterNum }} {{ 'printer' | pluralize(archivedPrinterNum) }} {{ $t("have been archived.") }}
                </div>
                <div>
                  <a href="/ent/printers/archived/" class="warning-action"
                    >{{ $t("Show Archived Printers") }}</a
                  >
                  <a class="warning-action" @click="handleNeverShowAgain">{{ $t("Never Show Again") }}</a>
                </div>
              </div>
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import sortBy from 'lodash/sortBy'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import { normalizedPrinter } from '@src/lib/normalizers'
import urls from '@config/server-urls'
import PrinterCard from '@src/components/printers/PrinterCard.vue'
import PageLayout from '@src/components/PageLayout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import SortingDropdown, { restoreSortingValue } from '@src/components/SortingDropdown'
import FilteringDropdown, { restoreFilterValues } from '@src/components/FilteringDropdown'
import { user, settings } from '@src/lib/page-context'
import ActiveFilterNotice from '@src/components/ActiveFilterNotice'
import i18n from '@src/i18n/i18n.js'

const SortingLocalStoragePrefix = 'printersSorting'
const SortingOptions = {
  options: [
    { title: `${i18n.t('Name')}`, key: 'name' },
    { title: `${i18n.t('Created at')}`, key: 'created_at' },
  ],
  default: { sorting: 'created_at', direction: 'desc' },
}

const FilterLocalStoragePrefix = 'printersFiltering'
const FilterOptions = {
  status: {
    title: `${i18n.t('Print Status')}`,
    queryParam: 'status',
    values: [
      { key: 'none', title: `${i18n.t('All Printers')}` },
      { key: 'online', title: `${i18n.t('Online Printers')}` },
      { key: 'active', title: `${i18n.t('Active Printers')}` },
    ],
    default: 'none',
  },
}

export default {
  name: 'PrinterListPage',

  components: {
    PrinterCard,
    PageLayout,
    CascadedDropdown,
    SortingDropdown,
    FilteringDropdown,
    ActiveFilterNotice,
  },

  data: function () {
    return {
      user: null,
      printers: [],
      loading: true,
      isEnt: false,
      archivedPrinterNum: 0,
      shouldShowArchiveWarning: false,

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
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return '\u221E'
      } else {
        return Math.round(this.user.dh_balance)
      }
    },
    mobileMenuOptions() {
      const options = [
        {
          key: 'sorting',
          icon: 'fas fa-sort-amount-down',
          title: `${this.$i18next.t(`Sort`)}`,
          expandable: true,
        },
        {
          key: 'filtering',
          icon: 'fas fa-filter',
          title: `${this.$i18next.t(`Filter`)}`,
          expandable: true,
        },
      ]

      if (this.isEnt) {
        options.unshift({
          key: 'dh',
          svgIcon: 'svg-hour-glass',
          title: `${this.$i18next.t(`{name} AI Detection Hours`,{name:this.dhBadgeNum})}`,
          href: '/user_preferences/dh/',
        })
      }

      return options
    },

    visiblePrinters() {
      let printers = this.printers
      switch (this.filterValues.status) {
        case 'online':
          printers = printers.filter((p) => !p.isDisconnected())
          break
        case 'active':
          printers = printers.filter((p) => p.isActive())
          break
        case 'none':
          break
      }

      if (this.sortingValue.sorting.key === 'created_at') {
        printers = sortBy(printers, (p) => p.createdAt())
      } else if (this.sortingValue.sorting.key === 'name') {
        printers = sortBy(printers, (p) => p.name)
      }

      if (this.sortingValue.direction.key === 'desc') {
        printers.reverse()
      }

      return printers
    },
    hiddenPrinterCount() {
      return this.printers.length - this.visiblePrinters.length
    },
  },

  created() {
    const { IS_ENT } = settings()
    this.isEnt = !!IS_ENT
    this.user = user()
    this.fetchPrinters()
  },

  methods: {
    fetchPrinters() {
      this.loading = true
      return axios
        .get(urls.printers(), {
          params: {
            with_archived: true,
          },
        })
        .then((response) => {
          const printers = response.data
          if (
            getLocalPref('single-printer-redirect-enabled', true) &&
            printers.length == 1 &&
            !printers[0].archived_at
          ) {
            window.location.href = `/printers/${printers[0].id}/control/`
            return
          }

          this.loading = false
          response.data.forEach((p) => {
            if (p.archived_at) {
              this.archivedPrinterNum += 1
            } else {
              this.insertPrinter(normalizedPrinter(p))
            }
          })
          this.shouldShowArchiveWarningFunc()
        })
    },
    insertPrinter(printer) {
      this.printers.push(printer)
    },
    onPrinterUpdated(printer) {
      let index = this.printers.findIndex((p) => p.id == printer.id)
      if (index < 0) {
        // FIXME any alert here?
        return
      }

      this.$set(this.printers, index, printer)
    },
    resetGcodesModal() {
      this.selectedGcodeId = null
      this.targetPrinter = null
    },

    // Sorting
    onSortingUpdated(sortingValue) {
      this.sortingValue = sortingValue
    },

    // Filtering
    onFilterUpdated(filterOptionKey, filterOptionValue) {
      this.filterValues[filterOptionKey] = filterOptionValue
    },
    resetFilters() {
      for (const key of Object.keys(this.filterValues)) {
        this.filterValues[key] = 'none'
        setLocalPref(`${FilterLocalStoragePrefix}-${key}`, 'none')
      }
    },
    handleNeverShowAgain() {
      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Are you sure?')}`,
        html: `<p style="text-align: center">${this.$i18next.t("You can always view your archived printers in by navigating to the General tab within Preferences.")}</p>`,
        showCancelButton: true,
        confirmButtonText: `${this.$i18next.t('Yes')}`,
        cancelButtonText: `${this.$i18next.t('No')}`,
      }).then((userAction) => {
        if (userAction.isConfirmed) {
          localStorage.setItem('shouldNeverShowArchived', JSON.stringify(true))
          this.shouldShowArchiveWarning = false
        }
      })
    },
    shouldShowArchiveWarningFunc() {
      const shouldNeverShow = localStorage.getItem('shouldNeverShowArchived')
      if (JSON.parse(shouldNeverShow) === true) {
        this.shouldShowArchiveWarning = false
      } else {
        this.shouldShowArchiveWarning = this.archivedPrinterNum > 0
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-list-page
  .consider-upgrade
    margin-bottom: var(--gap-between-blocks)

  .printer-cards
     margin-top: calc(var(--gap-between-blocks) * -1)

  .printer-card-wrapper
    margin-top: var(--gap-between-blocks)

  .bottom-messages
    margin-top: var(--gap-between-blocks)

  .warning
    display: flex
    flex-direction: row
    flex-wrap: wrap
    justify-content: space-between
    align-items: center

    .warning-action
      padding: 0.25em 0
      margin-left: auto
      margin: 0px 5px 0px 5px
      cursor: pointer

.btn.hours-btn
  position: relative
  color: var(--color-text-primary)

  .badge
    position: absolute
    left: 18px
    top: 4px
    border-radius: var(--border-radius-sm)
    background-color: var(--color-primary)
    height: auto
    font-size: .625rem

.custom-svg-icon
  height: 1.3rem
  width: 1.3rem

::v-deep .dropdown-item .clickable-area
  margin: -0.25rem -1.5rem
  padding: 0.25rem 1.5rem
</style>

<style lang="sass">
div[id^=b-modal-gcodes]
  .modal-header
    display: none
  .modal-body
    padding: 0
  .modal-footer
    display: none

#new-printer
  min-height: 25em
  .new-printer-container
    display: flex
    flex-flow: column
    align-items: center
    justify-content: center
    margin-top: 6em
    a
      text-align: center
      border: thin dashed
      color: var(--color-primary)
      border-color: var(--color-primary)
      padding: 4em 3em
      border-radius: var(--border-radius-lg)
      &:hover
        text-decoration: none
        background-color: var(--color-hover)
    .icon
      width: 2rem
      height: 2rem
      margin-bottom: 1rem
</style>
