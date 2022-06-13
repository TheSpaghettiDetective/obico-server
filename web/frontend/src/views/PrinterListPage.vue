<template>
  <layout>
    <template v-slot:topBarRight>
      <div>
        <a v-if="isEnt" href="/user_preferences/dh/" class="btn shadow-none hours-btn d-none d-md-inline" :title="dhBadgeNum + ' AI Detection Hours'">
          <svg>
            <use href="#svg-detective-hours"></use>
          </svg>
          <span id="user-credits" class="badge badge-light">{{dhBadgeNum}}</span>
          <span class="sr-only">AI Detection Hours</span>
        </a>
        <a href="/printers/wizard/" class="btn shadow-none icon-btn d-none d-md-inline" title="Link New Printer">
          <i class="fas fa-plus"></i>
        </a>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item v-if="isEnt" href="/user_preferences/dh/" class="d-md-none">
            <i class="fas fa-hourglass-half"></i>{{dhBadgeNum}} AI Detection Hours
          </b-dropdown-item>
          <b-dropdown-item href="/printers/wizard/" class="d-md-none">
            <i class="fas fa-plus"></i>Link New Printer
          </b-dropdown-item>
          <b-dropdown-divider class="d-md-none"></b-dropdown-divider>
          <cascaded-dropdown
            :menuOptions="menuOptions"
            :menuSelections="menuSelections"
            @menuSelectionChanged="menuSelectionChanged"
          >
          </cascaded-dropdown>
        </b-dropdown>
      </div>
    </template>

    <template v-slot:content>
      <div v-if="shouldShowFilterWarning" @click="onShowAllClicked" class="active-filter-notice">
        <div class="filter">
          <i class="fas fa-filter mr-2"></i>
          {{ activeFiltering }}
        </div>
        <a>SHOW ALL</a>
      </div>
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
            @PrinterUpdated="onPrinterUpdated"
            class="printer-card-wrapper"
          ></printer-card>
        </b-row>
        <div class="row justify-content-center">
          <div id="new-printer" class="col-sm-12 col-lg-6">
            <div class="new-printer-container">
              <a href="/printers/wizard/">
                <i class="fa fa-plus fa-2x"></i>
                <div>Link New Printer</div>
              </a>
            </div>
          </div>
        </div>
        <b-row v-show="shouldShowArchiveWarning" class="bottom-messages">
          <b-col>
            <div class="alert alert-warning alert-dismissible fade show mb-3" role="alert">
              <div class="warning">
                <div>{{ archivedPrinterNum }} {{ 'printer' | pluralize(archivedPrinterNum) }}
                  have been archived.</div>
                  <a
                    href="/ent/printers/archived/"
                    class="warning-action"
                  >Show Archived Printers</a>
                </div>
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'
import sortBy from 'lodash/sortBy'
import reverse from 'lodash/reverse'

import { getLocalPref, setLocalPref } from '@src/lib/pref'
import { normalizedPrinter } from '@src/lib/normalizers'

import urls from '@config/server-urls'
import PrinterCard from '@src/components/printers/PrinterCard.vue'
import Layout from '@src/components/Layout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import { user } from '@src/lib/page_context'

const SortIconClass = {
  asc: 'fas fa-long-arrow-alt-up',
  desc: 'fas fa-long-arrow-alt-down'
}

const LocalPrefNames = {
  StateFilter: 'printer-filtering',
  SortFilter: 'printer-sorting',
}

export default {
  name: 'PrinterListPage',
  components: {
    PrinterCard,
    Layout,
    CascadedDropdown,
  },
  created() {
    const {IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.isEnt = !!IS_ENT
    this.user = user()
    this.fetchPrinters()
  },
  data: function() {
    return {
      user: null,
      printers: [],
      loading: true,
      isEnt: false,
      menuSelections: {
        'Sort By': getLocalPref(
          LocalPrefNames.SortFilter,
          'by-date-desc'),
        'Filter By': getLocalPref(
          LocalPrefNames.StateFilter,
          'all'),
      },
      menuOptions: {
        'Sort By': {
          iconClass: 'fas fa-sort-amount-up',
          options: [
            {value: 'by-date-asc', title: 'Sort By Date', iconClass: SortIconClass['asc']},
            {value: 'by-date-desc', title: 'Sort By Date', iconClass: SortIconClass['desc']},
            {value: 'by-name-asc', title: 'Sort By Name', iconClass: SortIconClass['asc']},
            {value: 'by-name-desc', title: 'Sort By Name', iconClass: SortIconClass['desc']},
          ],
        },
        'Filter By': {
          iconClass: 'fas fa-filter',
          options: [
            {value: 'all', title: 'All Printers'},
            {value: 'online', title: 'Online Printers'},
            {value: 'active', title: 'Active Printers'},
          ],
        }
      },
      dontShowFilterWarning: false,
      archivedPrinterNum: 0,
    }
  },
  computed: {
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return'\u221E'
      } else {
        return Math.round(this.user.dh_balance)
      }
    },
    visiblePrinters() {
      let printers = this.printers
      switch (this.menuSelections['Filter By']) {
      case 'online':
        printers = printers.filter((p) => !p.isDisconnected())
        break
      case 'active':
        printers = printers.filter((p) => p.isPrinting())
        break
      case 'all':
        break
      }

      switch (this.menuSelections['Sort By']) {
      case 'by-date-asc':
        printers = sortBy(printers, (p) => p.createdAt())
        break
      case 'by-date-desc':
        printers = reverse(sortBy(printers, (p) => p.createdAt()))
        break
      case 'by-name-asc':
        printers = sortBy(printers, (p) => p.name)
        break
      case 'by-name-desc':
        printers = reverse(sortBy(printers, (p) => p.name))
        break
      }

      return printers
    },
    hiddenPrinterCount() {
      return this.printers.length - this.visiblePrinters.length
    },
    shouldShowFilterWarning() {
      return this.menuSelections['Filter By'] !== 'all'
    },
    shouldShowArchiveWarning() {
      return this.archivedPrinterNum > 0
    },
    activeFiltering() {
      const found = this.menuOptions['Filter By'].options.filter(option => option.value === this.menuSelections['Filter By'])
      return found.length ? found[0].title : null
    }
  },
  methods: {
    menuSelectionChanged(menu, selectedOption) {
      const val = selectedOption.value
      this.$set(this.menuSelections, menu, val)
      const prefName = menu === 'Sort By' ? LocalPrefNames.SortFilter : LocalPrefNames.StateFilter
      setLocalPref(prefName, val)
    },

    fetchPrinters() {
      this.loading = true
      return axios
        .get(urls.printers(), {
          params: {
            with_archived: true,
          }
        })
        .then(response => {
          this.loading = false
          response.data.forEach((p) => {
            if (p.archived_at) {
              this.archivedPrinterNum += 1
            } else {
              this.insertPrinter(normalizedPrinter(p))
            }
          })
        })
    },
    onShowAllClicked(){
      this.$set(this.menuSelections, 'Filter By', 'all')
      setLocalPref(
        LocalPrefNames.StateFilter,
        'all'
      )
    },
    insertPrinter(printer) {
      this.printers.push(printer)
    },

    onPrinterUpdated(printer) {
      let index = this.printers.findIndex(p => p.id == printer.id)
      if (index < 0) {
        // FIXME any alert here?
        return
      }

      this.$set(this.printers, index, printer)
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
      font-weight: bolder
      font-size: 1.1em
      margin-left: auto

.btn.hours-btn
  position: relative
  padding-right: 1.625rem
  color: var(--color-text-primary)

  svg
    height: 1.125rem
    width: 1.125rem

  .badge
    position: absolute
    left: 22px
    top: 8px
    border-radius: 4px
    background-color: var(--color-primary)
    height: auto
    font-size: .625rem

::v-deep .dropdown-item .clickable-area
  margin: -0.25rem -1.5rem
  padding: 0.25rem 1.5rem
</style>
