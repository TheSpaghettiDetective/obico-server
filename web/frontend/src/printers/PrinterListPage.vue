<template>
  <layout>
    <template v-slot:topBarRight>
      <div>
        <a v-if="isEnt" href="/ent/subscription/#detective-hour-balance" class="btn shadow-none hours-btn d-none d-md-inline" :title="dhBadgeNum + ' Detective Hours'">
          <svg viewBox="0 0 384 550">
            <use href="#svg-detective-hours"></use>
          </svg>
          <span id="user-credits" class="badge badge-light">{{dhBadgeNum}}</span>
          <span class="sr-only">Detective Hours</span>
        </a>
        <a href="/printers/wizard/" class="btn shadow-none icon-btn d-none d-md-inline" title="Link New Printer">
          <i class="fas fa-plus"></i>
        </a>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item v-if="isEnt" href="/ent/subscription/#detective-hour-balance" class="d-md-none">
            <i class="fas fa-hourglass-half"></i>{{dhBadgeNum}} Detective Hours
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
import Layout from '@common/Layout.vue'
import CascadedDropdown from '@common/CascadedDropdown'
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
    Layout,
    CascadedDropdown,
  },
  created() {
    const {IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.isEnt = !!IS_ENT
    this.user = user()
    this.StateFilter = StateFilter
    this.SortFilter = SortFilter
    this.SortOrder = SortOrder
    this.fetchPrinters()
  },
  data: function() {
    return {
      user: null,
      printers: [],
      loading: true,
      isEnt: false,
      menuSelections: {
        'Sort By': lookup(
            SortFilter,
            getLocalPref(
              LocalPrefNames.SortFilter,
              SortFilter.DateDesc),
            SortFilter.DateDesc
          ),
        'Filter By': lookup(
            StateFilter,
            getLocalPref(
              LocalPrefNames.StateFilter,
              StateFilter.All),
            StateFilter.All
          ),
      },
      menuOptions: {
        'Sort By': {
          iconClass: 'fas fa-sort-amount-up',
          options: [
            {value: SortFilter.DateAsc, title: 'Sort By Date', iconClass: SortIconClass[SortOrder.Asc]},
            {value: SortFilter.DateDesc, title: 'Sort By Date', iconClass: SortIconClass[SortOrder.Desc]},
            {value: SortFilter.NameAsc, title: 'Sort By Name', iconClass: SortIconClass[SortOrder.Asc]},
            {value: SortFilter.NameDesc, title: 'Sort By Name', iconClass: SortIconClass[SortOrder.Desc]},
          ],
        },
        'Filter By': {
          iconClass: 'fas fa-filter',
          options: [
            {value: StateFilter.All, title: 'All Printers'},
            {value: StateFilter.OnlineOnly, title: 'Online Printers Only'},
            {value: StateFilter.ActiveOnly, title: 'Active Printers Only'},
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
      case StateFilter.OnlineOnly:
        printers = printers.filter((p) => !p.isDisconnected())
        break
      case StateFilter.ActiveOnly:
        printers = printers.filter((p) => p.isPrinting())
        break
      case StateFilter.All:
        break
      }

      switch (this.menuSelections['Sort By']) {
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

          const signedUpLongerThan1Day = moment(this.user.date_joined).isBefore(moment().subtract(15,'days'))
          const expiredLongerThan15Days = this.user.subscription.expired_at && moment(this.user.subscription.expired_at).isBefore(moment().add(15,'days'))
          if (!this.user.is_pro && expiredLongerThan15Days && this.printers.length > 0 && Math.random() < 0.2) {
            this.$swal.Toast.fire({
              html: '<p style="margin: 0;">Please consider <a href="/ent_pub/pricing?utm_source=tsd&utm_medium=printers-page">upgrading</a> to support our development efforts! <a href="https://www.thespaghettidetective.com/docs/upgrade-to-pro#why-cant-the-detective-just-work-for-free-people-love-free-you-know" target="_new">Why?</a></p>',
            })
          } else if (this.isEnt && !this.user.is_primary_email_verified && signedUpLongerThan1Day) {
            this.$swal.Toast.fire({
              html: '<div><a href="/accounts/email/">Please verify your email address.</a></div><div>Otherise you will not get notified by email on print failures.</div>',
            })
          }
        })
    },
    onShowAllPrintersClicked(){
      this.$set(this.menuSelections, 'Filter By', StateFilter.All)
      setLocalPref(
        LocalPrefNames.StateFilter,
        StateFilter.All
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
      font-size: 1.1em
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
    background-color: var(--color-primary)
    height: auto
    font-size: .625rem

::v-deep .dropdown-item .clickable-area
  margin: -0.25rem -1.5rem
  padding: 0.25rem 1.5rem
</style>
