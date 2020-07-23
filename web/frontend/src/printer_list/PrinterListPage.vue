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
        :is-connecting="isConnecting(printer.id)"
        @DeleteClicked="onDeleteClicked(printer.id)"
        @NotAFailureClicked="onNotAFailureClicked($event, printer.id, false)"
        @WatchForFailuresToggled="onWatchForFailuresToggled(printer.id)"
        @PauseOnFailureToggled="onPauseOnFailureToggled(printer.id)"
        @ExpandThumbnailToFullClicked="onExpandThumbnailToFullClicked(printer.id)"
        @PrinterActionPauseClicked="onPrinterActionPauseClicked(printer.id)"
        @PrinterActionResumeClicked="onPrinterActionResumeClicked($event, printer.id)"
        @PrinterActionCancelClicked="onPrinterActionCancelClicked(printer.id)"
        @PrinterActionConnectClicked="onPrinterActionConnectClicked(printer.id)"
        @PrinterActionStartClicked="onPrinterActionStartClicked(printer.id)"
        @PrinterActionControlClicked="onPrinterActionControlClicked(printer.id)"
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
import moment from 'moment'
import filesize from 'filesize'
import get from 'lodash/get'
import sortBy from 'lodash/sortBy'
import reverse from 'lodash/reverse'
import filter from 'lodash/filter'

import { getLocalPref, setLocalPref } from '@lib/printers'
import { normalizedPrinter } from '@lib/normalizers'
import {
  shouldShowAlert,
  isPrinterDisconnected,
  printInProgress,
} from '@lib/printers'

import apis from '@lib/apis'
import PrinterWebSocket from '@lib/printer_ws'

import PrinterCard from './PrinterCard.vue'
import {PAUSE, NOPAUSE} from './PrinterCard.vue'
import StartPrint from './StartPrint.vue'
import ConnectPrinter from './ConnectPrinter.vue'

let printerDeleteUrl = printerId => `/printers/${printerId}/delete/`
let printerWSUrl = printerId => `/ws/web/${printerId}/`
let printerControlUrl = printerId => `/printers/${printerId}/control/`

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
    this.printerWs = PrinterWebSocket()
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
  props: {
    isProAccount: {
      type: Boolean,
      required: true
    }
  },
  data: function() {
    return {
      printers: [],
      localPrinterState: new Map(),
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
        printers = printers.filter((p) => !isPrinterDisconnected(get(p, 'status.state')))
        break
      case StateFilter.Active:
        printers = printers.filter((p) => printInProgress(get(p, 'status.state')))
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
      return axios
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
      this.$swal.Confirm({}).then((result) => {
        if (result.value) { // When it is confirmed
          window.location.href = printerDeleteUrl(printerId)
        }
      })
    },
    onNotAFailureClicked(event, printerId, resumePrint) {
      this.$swal.Confirm.fire({
        title: 'Noted!',
        html: '<p>Do you want The Detective to keep watching this print?</p><small>If you select "No", The Detective will stop watching this print, but will automatically resume watching on your next print.</small>',
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
      }).then((result) => {
        if (result.dismiss == 'cancel') {
          // Hack: So that 2 APIs are not called at the same time
          setTimeout(() => {
            this.sendPrinterAction(
              printerId,
              '/mute_current_print/?mute_alert=true',
              false
            )
          }, 1000)
        }
        if (resumePrint) {
          this.sendPrinterAction(
            printerId,
            '/resume_print/',
            true)
        } else {
          this.sendPrinterAction(
            printerId,
            '/acknowledge_alert/?alert_overwrite=NOT_FAILED',
            false)
        }
      })
      event.preventDefault()
    },
    onWatchForFailuresToggled(printerId) {
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.watching = !p.watching
        this.updatePrinter(p)
      }
    },
    onPauseOnFailureToggled(printerId) {
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.action_on_failure = p.action_on_failure == PAUSE ? NOPAUSE : PAUSE
        this.updatePrinter(p)
      }
    },
    onExpandThumbnailToFullClicked(printerId) {
      console.log('ExpandThumbnailToFullClicked', printerId) //FIXME
    },
    onPrinterActionPauseClicked(printerId) {
      this.sendPrinterAction(printerId, '/pause_print/', true)
    },
    onPrinterActionResumeClicked(event, printerId) {
      let printer = this.printers.find((p) => p.id == printerId)
      if (shouldShowAlert(printer)) {
        this.onNotAFailureClicked(event, printerId, true)
      } else {
        this.sendPrinterAction(printerId, '/resume_print/', true)
      }
    },
    onPrinterActionCancelClicked(printerId) {
      this.$swal.Confirm.fire({
        text: 'Once cancelled, the print can no longer be resumed.',
      }).then((result) => {
        if (result.value) {
          // When it is confirmed
          this.sendPrinterAction(printerId, '/cancel_print/', true)
        }
      })
    },
    onPrinterActionConnectClicked(printerId) {
      this.setIsConnecting(printerId, true)
      this.printerWs.passThruToPrinter(
        printerId,
        { func: 'get_connection_options', target: '_printer' },
        (err, connectionOptions) => {
          if (err) {
            this.$swal.Toast.fire({
              type: 'error',
              title: 'Failed to contact OctoPrint!',
            })
            this.setIsConnecting(printerId, false)
          } else {
            if (connectionOptions.ports.length < 1) {
              this.$swal.Toast.fire({
                type: 'error',
                title: 'Uh-Oh. No printer is found on the serial port.',
              })
              this.setIsConnecting(printerId, false)
            } else {
              this.$swal.openModalWithComponent(
                ConnectPrinter,
                {
                  connectionOptions: connectionOptions,
                },
                {
                  confirmButtonText: 'Connect',
                  showCancelButton: true,
                }
              ).then((result) => {
                if (result.value) {
                  let args = [
                    result.value.port,
                    result.value.baudrate
                  ]
                  this.printerWs.passThruToPrinter(
                    printerId,
                    { func: 'connect', target: '_printer',
                      args: args },
                    () => {
                      this.setIsConnecting(printerId, false)
                    }
                  )
                }
              })
            }
          }
        }
      )
    },
    onPrinterActionStartClicked(printerId) {
      if (!this.isProAccount) {
        this.$swal.fire({
          title: 'Wait!',
          html: `
              <h5 class="mb-3">You need to <a href="/ent/pricing/">upgrade to Pro plan</a> to start a remote print job. </h5>
              <p>Remote G-Code upload and print start is a Pro feature.</p>
              <p>With <a href="/ent/pricing/">little more than 1 Starbucks per month</a>, you can upgrade to a Pro account.</p>
            `
        })
        return
      }

      let printer = this.printers.find((p) => p.id == printerId)

      axios
        .get(
          '/api/v1/gcodes/',
        ).then((response) => {
          let gcodeFiles = response.data
          gcodeFiles.forEach(function (gcodeFile) {
            gcodeFile.created_at = moment(gcodeFile.created_at).fromNow()
            gcodeFile.num_bytes = filesize(gcodeFile.num_bytes)
          })

          this.$swal.openModalWithComponent(
            StartPrint,
            {
              gcodeFiles: gcodeFiles,
              onGcodeFileSelected: this.onGcodeFileSelected,
            },
            {
              title: 'Print on ' + printer.name,
              showConfirmButton: false,
              showCancelButton: true,
            }
          )
        })
    },
    onGcodeFileSelected(printerId, gcodeFiles, gcodeFileId) {
      // actionsDiv.find('button').attr('disabled', true) // TODO
      let printer = this.printers.find((p) => p.id == printerId)

      this.printerWs.passThruToPrinter(
        printerId,
        { func: 'download',
          target: 'file_downloader',
          args: filter(gcodeFiles, { id: gcodeFileId })
        },
        (err, ret) => {
          if (ret.error) {
            this.$swal.Toast.fire({
              type: 'error',
              title: ret.error,
            })
            return
          }

          let targetPath = ret.target_path

          let html =`
          <div class="text-center">
            <i class="fas fa-spinner fa-spin fa-lg py-3"></i>
            <h5 class="py-3">
              Uploading G-Code to ${printer.name} ...
            </h5>
            <p>
              ${targetPath}
            </p>
          </div>`

          this.$swal.fire({
            html: html,
            showConfirmButton: false
          })

          let checkPrinterStatus = () => {
            let updatedPrinter = this.printers.find((p) => p.id == printerId)
            if (get(updatedPrinter, 'status.state.text') == 'Operational') {
              setTimeout(checkPrinterStatus, 1000)
            } else {
              this.$swal.close()
            }
          }
          checkPrinterStatus()
        }
      )
    },
    onPrinterActionControlClicked(printerId) {
      window.location = printerControlUrl(printerId)
    },
    isConnecting(printerId) {
      let state = this.localPrinterState[printerId]
      if (state) {
        return state.isConnecting == true
      }
      return false
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
    sendPrinterAction(printerId, path, someBool) {
      console.log('sendPrinterAction', printerId, path, someBool) // TODO
    },
    setIsConnecting(printerId, isConnecting) {
      let state = this.localPrinterState[printerId] || {}
      state.isConnecting = isConnecting
      this.localPrinterState[printerId] = state
    },
  },
  mounted() {
    this.fetchPrinters().then(() => {
      // var wsUri = printerCard.data('share-token') ? // TODO
      // '/ws/shared/web/' + printerCard.data('share-token') + '/' :
      this.printers.forEach((printer) => {
        this.printerWs.openPrinterWebSockets(
          printer.id,
          printerWSUrl(printer.id),
          (data) => {
            this.printers.map(p => {
              if (p.id == data.id) {
                return normalizedPrinter(data)
              }
              return p
            })
          }
        )
      })
    })
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
