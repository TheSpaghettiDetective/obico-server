<template>
  <div id="print-list-page">
    <div class="option-drawer">
      <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
        <div class="panel panel-default">
          <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
            <div class="panel-body p-3">
              <div>
                <div class="sorting-and-filter">
                  <select
                    id="printer-sorting"
                    class="my-1 mx-2"
                    v-model="filters.sort"
                    @change="onSortFilterChanged()"
                  >
                    <option
                      v-for="item in sortFilters"
                      :key="item.id"
                      :value="item.id"
                    >{{ item.title }}
                      <i
                        v-if="item.order == SortOrder.Asc"
                        class="fas fa-long-arrow-alt-up"
                      ></i>
                      <i
                        v-if="item.order == SortOrder.Desc"
                        class="fas fa-long-arrow-alt-down"
                      ></i>
                    </option>
                  </select>

                  <select
                    id="printer-filtering"
                    class="my-1 mx-2"
                    v-model="filters.state"
                    @change="onStateFilterChanged()"
                  >
                    <option
                      v-for="item in stateFilters"
                      :key="item.id"
                      :value="item.id"
                    >{{ item.title }}</option>
                  </select>
                </div>
              </div>
              <hr />
              <div>
                <a
                  v-for="printer in visiblePrinters"
                  :key="printer.id"
                  :href="'#' + printer.id"
                  role="button"
                  class="btn btn-outline-primary btn-sm my-1 mx-2 printer-link">
                  <i class="fas fa-map-pin"></i>&nbsp;&nbsp;{{ printer.name }}
                </a>
              </div>
            </div>
          </div>
          <div class="panel-heading" role="tab" id="headingOne">
            <div class="panel-title">
              <button class="btn btn-block shadow-none" role="button" data-toggle="collapse" data-parent="#accordion"
                href="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                <i class="fas fa-angle-down"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="printers" class="row justify-content-center">
      <b-spinner v-if="loading" label="Loading..."></b-spinner>
      <PrinterCard
        v-for="printer in visiblePrinters"
        :key="printer.id"
        :printer="printer"
        :is-on-shared-page="isOnSharedPage"
        @DeleteClicked="onDeleteClicked(printer.id)"
        @NotAFailureClicked="onNotAFailureClicked(printer.id, false)"
        @WatchForFailuresToggled="onWatchForFailuresToggled(printer.id)"
        @PauseOnFailureToggled="onPauseOnFailureToggled(printer.id)"
        @ExpandThumbnailToFullClicked="onExpandThumbnailToFullClicked(printer.id)"
      ></PrinterCard>
    </div>

    <div class="row justify-content-center">
      <div id="new-printer" class="col-sm-12 col-lg-6">
        <div class="new-printer-container">
          <a href="/printers/new">
            <i class="fa fa-plus fa-2x"></i>
            <div>Add Printer</div>
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

import get from 'lodash/get'
import sortBy from 'lodash/sortBy'
import reverse from 'lodash/reverse'

import { getLocalPref, setLocalPref } from '@lib/printers'
import { normalizedPrinter } from '@lib/normalizers'
import * as plib from '@lib/printers'
import apis from '@lib/apis'

import PrinterCard from './PrinterCard.vue'
import {PAUSE, NOPAUSE} from './PrinterCard.vue'


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

const LocalPrefNames = {
  StateFilter: 'printer-filtering',
  SortFilter: 'printer-sorting',
}

let lookup = (obj, value, def)=> {
  console.log(obj, value, def)
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
  },
  created() {
    this.StateFilter = StateFilter
    this.SortFilter = SortFilter
    this.SortOrder = SortOrder
    this.stateFilters = [
      {id: StateFilter.All, title: 'All'},
      {id: StateFilter.OnlineOnly, title: 'Online Printers Only'},
      {id: StateFilter.ActiveOnly, title: 'Active Printers Only'},
    ]
    this.sortFilters = [
      {id: SortFilter.DateAsc, title: 'By Date Asc', order: SortOrder.Asc},
      {id: SortFilter.DateDesc, title: 'By Date Desc', order: SortOrder.Desc},
      {id: SortFilter.NameAsc, title: 'By Name Asc', order: SortOrder.Asc},
      {id: SortFilter.NameDesc, title: 'By Name Desc', order: SortOrder.Desc},
    ]
  },
  data: function() {
    return {
      printers: [],
      loading: false,
      isOnSharedPage: false,
      filters: {
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
      }
    }
  },
  computed: {
    visiblePrinters() {
      let printers = this.printers
      switch (this.filters.state) {
      case StateFilter.OnlineOnly:
        printers = printers.filter((p) => !plib.isPrinterDisconnected(get(p, 'status.state')))
        break
      case StateFilter.Active:
        printers = printers.filter((p) => plib.printInProgress(get(p, 'status.state')))
        break
      case StateFilter.All:
        break
      }

      switch (this.filters.sort) {
      case SortFilter.DateAsc:
        printers = sortBy(printers, (p) => p.created_at)
        break
      case SortFilter.DateDesc:
        printers = reverse(sortBy(printers, (p) => p.created_at))
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
    }
  },
  methods: {
    // TODO
    //$('.option-drawer .printer-link').on('click', function() {
    //
    //    $('.panel-collapse').collapse('hide');
    //});
    fetchPrinters() {
      this.loading = true
      axios
        .get(apis.printers(), {
          params: {
            filter: this.filters.state,
            sorting: this.filters.sort
          }
        })
        .then(response => {
          this.loading = false
          this.printers = response.data.map(p => normalizedPrinter(p))
        })
    },
    onSortFilterChanged() {
      setLocalPref(
        LocalPrefNames.SortFilter,
        this.filters.sort
      )
    },
    onStateFilterChanged() {
      setLocalPref(
        LocalPrefNames.StateFilter,
        this.filters.state
      )
    },
    onShowAllPrintersClicked(){
      this.filters.state = StateFilter.All
      setLocalPref(
        LocalPrefNames.StateFilter,
        this.filters.state
      )
    },
    onDeleteClicked(printerId) {
      console.log(printerId) // TODO
    },
    onNotAFailureClicked(printerId, resumePrint) {
      let sendPrinterAction = (printerId, path, someBool) => {
        console.log('sendPrinterAction', printerId, path, someBool) // TODO
      }

      this.$swal.Confirm.fire({
        title: 'Noted!',
        html: '<p>Do you want The Detective to keep watching this print?</p><small>If you select "No", The Detective will stop watching this print, but will automatically resume watching on your next print.</small>',
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
      }).then((result) => {
        if (result.dismiss == 'cancel') {
          // Hack: So that 2 APIs are not called at the same time
          setTimeout(() => {
            sendPrinterAction(
              printerId,
              '/mute_current_print/?mute_alert=true',
              false
            )
          }, 1000)
        }
        if (resumePrint) {
          sendPrinterAction(
            printerId,
            '/resume_print/',
            true)
        } else {
          sendPrinterAction(
            printerId,
            '/acknowledge_alert/?alert_overwrite=NOT_FAILED',
            false)
        }
      })
    },
    onWatchForFailuresToggled(printerId) {
      console.log('watchtoggle', printerId)
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.watching = !p.watching
        this.updatePrinter(p)
      }
    },
    onPauseOnFailureToggled(printerId) {
      console.log('pausetoggle', printerId)
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.action_on_failure = p.action_on_failure == PAUSE ? NOPAUSE : PAUSE
        this.updatePrinter(p)
      }
    },
    onExpandThumbnailToFullClicked(printerId) {
      console.log('ExpandThumbnailToFullClicked', printerId) //FIXME
    },
    updatePrinter(printer) {
      return axios
        .patch(
          apis.printer(printer.id),
          {
            watching: printer.watching,
            action_on_failure: printer.action_on_failure,
          })
        .then(response => {
          this.printers.map(p => {
            if (p.id == response.data.id) {
              return normalizedPrinter(response.data)
            }
            return p
          })
        })
        .catch(response => {
          console.log(response)
          alert('Something went wrong!') // FIXME
        })
    },
  },
  mounted() {
    this.fetchPrinters()
  }
}
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@use "~main/theme"

#printer-list-page
  margin-top: 1.5rem

.menu-bar
  background-color: darken(theme.$color-bg-dark, 10)
  padding: 0.75rem
</style>
