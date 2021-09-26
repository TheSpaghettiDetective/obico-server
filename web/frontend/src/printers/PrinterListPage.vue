<template>
  <layout ref="layout">
    <template v-slot:desktopActions>
      <a href="/ent/subscription/#detective-hour-balance" class="btn shadow-none hours-btn" :title="dhBadgeNum + ' Detective Hours'">
        <svg viewBox="0 0 384 550">
          <use href="#svg-detective-hours"></use>
        </svg>
        <span id="user-credits" class="badge badge-light">{{dhBadgeNum}}</span>
        <span class="sr-only">Detective Hours</span>
      </a>
      <a href="/printers/wizard/" class="btn shadow-none icon-btn" title="Link New Printer">
        <i class="fas fa-plus"></i>
      </a>
    </template>
    <template v-slot:mobileActions>
      <b-dropdown-item href="/ent/subscription/#detective-hour-balance">
        <i class="fas fa-hourglass-half"></i>{{dhBadgeNum}} Detective Hours
      </b-dropdown-item>
      <b-dropdown-item href="/printers/wizard/">
        <i class="fas fa-plus"></i>Link New Printer
      </b-dropdown-item>
    </template>
    <template v-slot:sort>
      <b-dropdown-item v-for="option in sortFilters" :key="option.value">
        <div @click="updateSort(option.value); $refs.layout.sortOpened = false;" class="clickable-area">
          <i class="fas fa-check text-primary" :style="{visibility: filters.sort === option.value ? 'visible' : 'hidden'}"></i>
          {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
        </div>
      </b-dropdown-item>
    </template>
    <template v-slot:filter>
      <b-dropdown-item v-for="option in stateFilters" :key="option.value">
        <div @click="updateFilter(option.value); $refs.layout.filterOpened = false;" class="clickable-area">
          <i class="fas fa-check text-primary" :style="{visibility: filters.state === option.value ? 'visible' : 'hidden'}"></i>
          {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
        </div>
      </b-dropdown-item>
    </template>
    <template v-slot:content>
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
                <div>Link OctoPrint Printer</div>
              </a>
            </div>
          </div>
        </div>
        <b-row v-show="shouldShowFilterWarning || shouldShowArchiveWarning" class="bottom-messages">
          <b-col>
            <div v-if="shouldShowFilterWarning" class="alert alert-warning alert-dismissible fade show mb-3" role="alert">
              <div class="warning">
                <div>{{ hiddenPrinterCount }} {{ 'printer' | pluralize(hiddenPrinterCount) }}
                  hidden by the filter.</div>
                  <a
                    role="button"
                    href="#"
                    class="warning-action"
                    @click="onShowAllPrintersClicked()"
                  >Show All Printers</a>
                </div>
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div v-if="shouldShowArchiveWarning" class="alert alert-warning alert-dismissible fade show mb-3" role="alert">
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
import moment from 'moment'

import { getLocalPref, setLocalPref } from '@lib/pref'
import { normalizedPrinter } from '@lib/normalizers'

import urls from '@lib/server_urls'
import PrinterCard from './PrinterCard.vue'
// import Select from '@common/Select.vue'
import Layout from '@common/Layout.vue'
import { user } from '@lib/page_context'

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
    // Select,
    Layout,
  },
  created() {
    this.user = user()

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
    shouldShowFilterWarning() {
      return this.hiddenPrinterCount > 0 && !this.dontShowFilterWarning
    },
    shouldShowArchiveWarning() {
      return this.archivedPrinterNum > 0
    },
  },
  methods: {
    updateSort(newSort) {
      this.filters.sort = newSort
      setLocalPref(
        LocalPrefNames.SortFilter,
        this.filters.sort
      )
    },
    updateFilter(newFilter) {
      this.filters.state = newFilter
      setLocalPref(
        LocalPrefNames.StateFilter,
        this.filters.state
      )
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

          const signedUpLongerThan1Day = moment(this.user.date_joined).isBefore(moment().subtract(15,'days'))
          const expiredLongerThan15Days = this.user.subscription.expired_at && moment(this.user.subscription.expired_at).isBefore(moment().add(15,'days'))
          if (!this.user.is_pro && expiredLongerThan15Days && this.printers.length > 0 && Math.random() < 0.2) {
            this.$swal.Toast.fire({
              html: '<p style="margin: 0;">Please consider <a href="/ent/pricing?utm_source=tsd&utm_medium=printers-page">upgrading</a> to support our development efforts.</p><p><a href="https://www.thespaghettidetective.com/docs/upgrade-to-pro#why-cant-the-detective-just-work-for-free-people-love-free-you-know" target="_new">Learn more >>></a></p>',
            })
          } else if (this.isEnt && !this.user.is_primary_email_verified && signedUpLongerThan1Day) {
            this.$swal.Toast.fire({
              html: '<div><a href="/accounts/email/">Please verify your email address.</a></div><div>Otherise you will not get notified by email on print failures.</div>',
            })
          }
        })
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

<style lang="sass" scoped>
@use "~main/theme"

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
      font-size: 1.125em
      margin-left: auto

.btn.hours-btn
  position: relative
  padding-right: 1.625rem

  svg
    height: 1.125rem
    width: auto

  .badge
    position: absolute
    left: 22px
    top: 8px
    border-radius: 4px
    background-color: rgb(var(--color-primary))
    height: auto
    font-size: .625rem

::v-deep .dropdown-item .clickable-area
  margin: -0.25rem -1.5rem
  padding: 0.25rem 1.5rem
</style>
