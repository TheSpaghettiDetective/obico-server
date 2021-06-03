<template>
  <div>
    <pull-to-reveal
      :shiftContent="true"
      :showEdge="true"
      :enable="printers.length > 0"
      @hide="closeMenus"
    >
      <navbar
        view-name="printers"
        ref="navbar"
      ></navbar>
      <div v-if="printers.length > 1" class="container">
        <div class="option-drawer">
          <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
            <div class="panel panel-default">
              <div
                id="collapse-one"
                class="panel-collapse in"
                role="tabpanel"
                aria-labelledby="headingOne"
              >
                <div class="panel-body p-3">
                  <div>
                    <div class="sorting-and-filter" ref="filters">
                      <Select
                        id="printer-sorting"
                        class="my-1 mx-2"
                        v-model="filters.sort"
                        :options="sortFilters"
                        @input="onSortFilterChanged()"
                      ></Select>

                      <Select
                        id="printer-filtering"
                        class="my-1 mx-2"
                        v-model="filters.state"
                        :options="stateFilters"
                        @input="onStateFilterChanged()"
                      ></Select>
                    </div>
                  </div>
                  <hr />
                  <div>
                    <a
                      v-for="printer in visiblePrinters"
                      :key="printer.id"
                      :href="'#' + printer.id"
                      role="button"
                      class="btn btn-outline-primary btn-sm my-1 mx-3 printer-link">
                      <i class="fas fa-map-pin"></i>&nbsp;&nbsp;{{ printer.name }}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </pull-to-reveal>

    <div v-if="!user.is_pro && printers.length > 0" class="row justify-content-center">
      <div class="col-sm-12 col-lg-6">
        <div class="form-container" style="margin: 1em 0 -1em 0; padding: 0.5em 1em;">
          <p style="margin: 0;">Please consider <a href="/ent/pricing?utm_source=tsd&utm_medium=printers-page">upgrading</a> to support our development efforts! <a href="https://help.thespaghettidetective.com/kb/guide/en/free-plan-vs-pro-plan-My6yGUkT4T/Steps/294248,294251,294249,294250" target="_new">Why?</a></p>
        </div>
      </div>
    </div>

    <div id="printers" class="row justify-content-center pt-2">
      <b-spinner v-if="loading" class="mt-5" label="Loading..."></b-spinner>
      <printer-card
        v-for="printer in visiblePrinters"
        :key="printer.id"
        :printer="printer"
        :is-pro-account="user.is_pro"
        @PrinterUpdated="onPrinterUpdated"
      ></printer-card>
    </div>

    <div class="row justify-content-center">
      <div id="new-printer" class="col-sm-12 col-lg-6">
        <div class="new-printer-container">
          <a href="/printers/wizard/">
            <i class="fa fa-plus fa-2x"></i>
            <div>Link OctoPrint Printer</div>
          </a>
        </div>
      </div>
    </div>

    <div
      v-if="hiddenPrinterCount > 0"
      id="printers-hidden-warning"
      class="text-warning border-warning text-center border my-3 py-2"
    >
      <span id="printers-hidden">{{ hiddenPrinterCount }}</span> printers are
      hidden by the filtering settings.&nbsp;&nbsp;
      <a
        href="#"
        id="show-all-printers-btn"
        @click="onShowAllPrintersClicked()"
      >Show all printers >>></a>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import sortBy from 'lodash/sortBy'
import reverse from 'lodash/reverse'

import { getLocalPref, setLocalPref } from '@lib/pref'
import { normalizedPrinter } from '@lib/normalizers'

import urls from '@lib/server_urls'
import PrinterCard from './PrinterCard.vue'
import Select from '@common/Select.vue'
import Navbar from '@common/Navbar.vue'
import PullToReveal from '@common/PullToReveal.vue'

const SortOrder = {
  Asc: 'asc',
  Desc: 'desc'
}

const StateFilter = {
  All: 'all',
  OnlineOnly: 'online',
  ActiveOnly: 'active',
}

const SortFilter = {
  DateAsc: 'by-date-asc',
  DateDesc: 'by-date-desc',
  NameAsc: 'by-name-asc',
  NameDesc: 'by-name-desc',
}

const SortIconClass = {
  [SortOrder.Asc]: 'fas fa-long-arrow-alt-up',
  [SortOrder.Desc]: 'fas fa-long-arrow-alt-down'
}

const LocalPrefNames = {
  StateFilter: 'printer-filtering',
  SortFilter: 'printer-sorting',
}

let lookup = (obj, value, def)=> {
  const ret = Object.entries(obj).find(pair => (pair[1] == value))
  if (ret) {
    return ret[1]
  } else {
    return def
  }
}

export default {
  name: 'PrinterListPage',
  components: {
    PrinterCard,
    Select,
    Navbar,
    PullToReveal,
  },
  created() {
    this.user = JSON.parse(document.querySelector('#user-json').text)

    this.StateFilter = StateFilter
    this.SortFilter = SortFilter
    this.SortOrder = SortOrder
    this.stateFilters = [
      {value: StateFilter.All, title: 'All Printers'},
      {value: StateFilter.OnlineOnly, title: 'Online Printers Only'},
      {value: StateFilter.ActiveOnly, title: 'Active Printers Only'},
    ]
    this.sortFilters = [
      {value: SortFilter.DateAsc, title: 'Sort By Date', iconClass: SortIconClass[SortOrder.Asc]},
      {value: SortFilter.DateDesc, title: 'Sort By Date', iconClass: SortIconClass[SortOrder.Desc]},
      {value: SortFilter.NameAsc, title: 'Sort By Name', iconClass: SortIconClass[SortOrder.Asc]},
      {value: SortFilter.NameDesc, title: 'Sort By Name', iconClass: SortIconClass[SortOrder.Desc]},
    ]

    this.fetchPrinters()
  },
  data: function() {
    return {
      user: null,
      printers: [],
      loading: true,
      filters: {
        visible: false,
        state: lookup(
          StateFilter,
          getLocalPref(
            LocalPrefNames.StateFilter,
            StateFilter.All),
          StateFilter.All
        ),
        sort: lookup(
          SortFilter,
          getLocalPref(
            LocalPrefNames.SortFilter,
            SortFilter.DateDesc),
          SortFilter.DateDesc
        )
      },
    }
  },
  computed: {
    visiblePrinters() {
      let printers = this.printers
      switch (this.filters.state) {
      case StateFilter.OnlineOnly:
        printers = printers.filter((p) => !p.isDisconnected())
        break
      case StateFilter.ActiveOnly:
        printers = printers.filter((p) => p.isPrinting())
        break
      case StateFilter.All:
        break
      }

      switch (this.filters.sort) {
      case SortFilter.DateAsc:
        printers = sortBy(printers, (p) => p.createdAt())
        break
      case SortFilter.DateDesc:
        printers = reverse(sortBy(printers, (p) => p.createdAt()))
        break
      case SortFilter.NameAsc:
        printers = sortBy(printers, (p) => p.name)
        break
      case SortFilter.NameDesc:
        printers = reverse(sortBy(printers, (p) => p.name))
        break
      }

      return printers
    },
    hiddenPrinterCount() {
      return this.printers.length - this.visiblePrinters.length
    },

  },
  methods: {
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
              this.$swal.Toast.fire({
                html: '<br /><h6>Some of your printers have been archived.</h6><p><a href="/ent/printers/archived/">Find them here.</a></p>',
                timer: 15000,
              })
            } else {
              this.insertPrinter(normalizedPrinter(p))
            }
          })
        })
    },
    toggleFiltersPanel() {
      this.filters.visible = !this.filters.visible
    },
    onSortFilterChanged() {
      setLocalPref(
        LocalPrefNames.SortFilter,
        this.filters.sort
      )
      this.toggleFiltersPanel()
    },
    onStateFilterChanged() {
      setLocalPref(
        LocalPrefNames.StateFilter,
        this.filters.state
      )
      this.toggleFiltersPanel()
    },
    onShowAllPrintersClicked(){
      this.filters.state = StateFilter.All
      setLocalPref(
        LocalPrefNames.StateFilter,
        this.filters.state
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

    closeMenus() {
      this.$refs.navbar.hideDropdowns()

      if (this.$refs.filters) {
        const dropdowns = this.$refs.filters.querySelectorAll('.dropdown')
        dropdowns.forEach(dropdown => {
          if (dropdown.classList.contains('show')) {
            dropdown.classList.remove('show')
            dropdown.querySelector('.dropdown-menu').classList.remove('show')
          }
        })
      }
    }
  },
}
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@use "~main/theme"

#printer-list-page
  margin-top: 1.5rem

.menu-bar
  background-color: rgb(var(--color-bg-dark-d-10))
  padding: 0.75rem
</style>
