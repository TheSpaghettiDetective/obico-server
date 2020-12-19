<template>
  <div>
    <div class="option-drawer">
      <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
        <div class="panel panel-default">
          <b-collapse
            id="collapse-one"
            v-model="filters.visible"
            class="panel-collapse in"
            role="tabpanel"
            aria-labelledby="headingOne"
          >
            <div class="panel-body p-3">
              <div>
                <div class="sorting-and-filter">
                  <TSDSelect
                    id="printer-sorting"
                    class="my-1 mx-2"
                    v-model="filters.sort"
                    :options="sortFilters"
                    @input="onSortFilterChanged()"
                  ></TSDSelect>

                  <TSDSelect
                    id="printer-filtering"
                    class="my-1 mx-2"
                    v-model="filters.state"
                    :options="stateFilters"
                    @input="onStateFilterChanged()"
                  ></TSDSelect>
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
          </b-collapse>
          <div class="panel-heading" role="tab" id="headingOne">
            <div class="panel-title">
              <button
                class="btn btn-block shadow-none"
                role="button"
                @click="toggleFiltersPanel"
              ><i class="fas fa-angle-down"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isProAccount" class="row justify-content-center">
      <div class="col-sm-12 col-lg-6">
        <div class="form-container" style="margin: 1em 0 -1em 0; padding: 0.5em 1em;">
          <p style="margin: 0;">Please consider <a href="/ent/pricing?utm_source=tsd&utm_medium=printers-page">upgrading</a> to support our development efforts! <a href="https://www.thespaghettidetective.com/docs/upgrade-to-pro/#what-cant-the-detective-just-work-for-free-people-love-free-you-know" target="_new">Why?</a></p>
        </div>
      </div>
    </div>

    <div id="printers" class="row justify-content-center">
      <b-spinner v-if="loading" class="mt-5" label="Loading..."></b-spinner>
      <printer-card
        v-for="printer in visiblePrinters"
        ref="printer"
        :key="printer.id"
        :printer="printer"
        :is-pro-account="isProAccount"
        @NotAFailureClicked="onNotAFailureClicked($event, printer.id, false)"
        @WatchForFailuresToggled="onWatchForFailuresToggled(printer.id)"
        @PauseOnFailureToggled="onPauseOnFailureToggled(printer.id)"
        @PrinterActionPauseClicked="onPrinterActionPauseClicked(printer.id)"
        @PrinterActionResumeClicked="onPrinterActionResumeClicked($event, printer.id)"
        @PrinterActionCancelClicked="onPrinterActionCancelClicked(printer.id)"
        @PrinterActionConnectClicked="onPrinterActionConnectClicked(printer.id)"
        @PrinterActionStartClicked="onPrinterActionStartClicked(printer.id)"
        @PrinterActionControlClicked="onPrinterActionControlClicked(printer.id)"
        @TempEditClicked="onTempEditClicked(printer.id, $event)"
      ></printer-card>
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

import { getLocalPref, setLocalPref } from '@lib/pref'
import { normalizedPrinter } from '@lib/normalizers'

import urls from '@lib/server_urls'
import PrinterWebSocket from '@lib/printer_ws'

import PrinterCard from './PrinterCard.vue'
import StartPrint from './StartPrint.vue'
import ConnectPrinter from './ConnectPrinter.vue'
import TempTargetEditor from './TempTargetEditor.vue'
import TSDSelect from '@common/TSDSelect.vue'

const PAUSE_PRINT = '/pause_print/'
const RESUME_PRINT = '/resume_print/'
const CANCEL_PRINT = '/cancel_print/'
const MUTE_CURRENT_PRINT = '/mute_current_print/?mute_alert=true'
const ACK_ALERT_NOT_FAILED = '/acknowledge_alert/?alert_overwrite=NOT_FAILED'

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
    TSDSelect
  },
  created() {
    this.printerWs = PrinterWebSocket()
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
  },
  props: {
    isProAccount: {
      type: Boolean,
      required: true
    },
  },
  data: function() {
    return {
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
        printers = printers.filter((p) => !p.isDisconnected)
        break
      case StateFilter.ActiveOnly:
        printers = printers.filter((p) => p.isPrinting)
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
    onNotAFailureClicked(ev, printerId, resumePrint) {
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
              MUTE_CURRENT_PRINT,
              false
            )
          }, 1000)
        }
        if (resumePrint) {
          this.sendPrinterAction(
            printerId,
            RESUME_PRINT,
            true)
        } else {
          this.sendPrinterAction(
            printerId,
            ACK_ALERT_NOT_FAILED,
            false)
        }
      })

      ev.preventDefault()
    },
    onWatchForFailuresToggled(printerId) {
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.watching_enabled = !p.watching_enabled
        this.updatePrinter(p)
      }
    },
    onPauseOnFailureToggled(printerId) {
      let p = this.printers.find((p) => p.id == printerId)
      if (p) {
        p.action_on_failure = p.action_on_failure == 'PAUSE' ? 'NONE' : 'PAUSE'
        this.updatePrinter(p)
      }
    },
    onPrinterActionPauseClicked(printerId) {
      this.$swal.Confirm.fire({
        html: 'If you haven\'t changed the default configuration, the heaters will be turned off, and the print head will be z-lifted. The reversed will be performed before the print is resumed. <a target="_blank" href="https://www.thespaghettidetective.com/docs/detection-print-job-settings/#when-print-is-paused">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a>',
      }).then((result) => {
        if (result.value) {
          this.sendPrinterAction(printerId, PAUSE_PRINT, true)
        }
      })
    },
    onPrinterActionResumeClicked(ev, printerId) {
      let printer = this.printers.find((p) => p.id == printerId)
      if (printer.alertUnacknowledged) {
        this.onNotAFailureClicked(ev, printerId, true)
      } else {
        this.sendPrinterAction(printerId, RESUME_PRINT, true)
      }
    },
    onPrinterActionCancelClicked(printerId) {
      this.$swal.Confirm.fire({
        text: 'Once cancelled, the print can no longer be resumed.',
      }).then((result) => {
        if (result.value) {
          // When it is confirmed
          this.sendPrinterAction(printerId, CANCEL_PRINT, true)
        }
      })
    },
    onPrinterActionConnectClicked(printerId) {
      this.printerWs.passThruToPrinter(
        printerId,
        { func: 'get_connection_options', target: '_printer' },
        (err, connectionOptions) => {
          if (err) {
            this.$swal.Toast.fire({
              icon: 'error',
              title: 'Failed to connect!',
            })
          } else {
            if (connectionOptions.ports.length < 1) {
              this.$swal.Toast.fire({
                icon: 'error',
                title: 'Uh-Oh. No printer is found on the serial port.',
              })
            } else {
              this.$swal.openModalWithComponent(
                ConnectPrinter,
                {
                  connectionOptions: connectionOptions,
                },
                {
                  confirmButtonText: 'Connect',
                  showCancelButton: true,
                  preConfirm: () => {
                    return {
                      port: document.getElementById('connect-port').value,
                      baudrate: document.getElementById('connect-baudrate').value
                    }
                  }
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
                      args: args }
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
          urls.gcodes(),
        ).then((response) => {
          let gcodeFiles = response.data
          gcodeFiles.forEach(function (gcodeFile) {
            gcodeFile.created_at = moment(gcodeFile.created_at).fromNow()
            gcodeFile.num_bytes = filesize(gcodeFile.num_bytes)
          })

          this.$swal.openModalWithComponent(
            StartPrint,
            {
              printerId: printerId,
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
          if (err || ret.error) {
            this.$swal.Toast.fire({
              icon: 'error',
              title: err ? err : ret.error,
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
      window.location = urls.printerControl(printerId)
    },

    onTempEditClicked(printerId, item) {
      let printer = this.printers.find((p) => p.id == printerId)
      let tempProfiles = get(printer, 'settings.temp_profiles', [])
      let presets
      let maxTemp = 350

      if (item.key == 'bed') {
        presets = tempProfiles.map(
          (v) => {return {name: v.name, target: v['bed']}}
        )
        maxTemp = 140
      } else {
        presets = tempProfiles.map(
          (v) => {return {name: v.name, target: v['extruder']}}
        )
      }

      this.$swal.openModalWithComponent(
        TempTargetEditor,
        {
          presets: presets,
          maxTemp: maxTemp,
          curTarget: item.target,
        },
        {
          title: 'Set ' + item.toolName + ' Temperature',
          confirmButtonText: 'Confirm',
          showCancelButton: true,
          preConfirm: () => {
            return {
              target: parseInt(document.getElementById('target-temp').value)
            }
          }
        }).then((result) => {
        if (result.value) {
          let targetTemp = result.value.target
          this.printerWs.passThruToPrinter(
            printer.id,
            {
              func: 'set_temperature',
              target: '_printer',
              args: [item.key, targetTemp]
            })
        }
      })
    },

    updatePrinter(printer) {
      return axios
        .patch(
          urls.printer(printer.id),
          {
            watching_enabled: printer.watching_enabled,
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
          this.$swal.Toast.fire({
            icon: 'error',
            title: 'Failed to update printer!',
          }) // FIXME this was not handled in original code. sentry?
        })
    },

    sendPrinterAction(printerId, path, isOctoPrintCommand) {
      axios
        .get(urls.printerAction(printerId, path))
        .then(() => {
          let toastHtml = ''
          if (isOctoPrintCommand) {
            toastHtml += '<h6>Successfully sent command to OctoPrint!</h6>' +
                  '<p>It may take a while to be executed by OctoPrint.</p>'
          }
          if (toastHtml != '') {
            this.$swal.Toast.fire({
              icon: 'success',
              html: toastHtml,
            })
          }
        })
    },

    shouldVideoBeFull(printer) {
      let hasImage = get(printer, 'pic.img_url')
      let shouldBeThumb = printer.alertUnacknowledged && hasImage
      return !shouldBeThumb
    },

    insertPrinter(printer) {
      this.printers.push(printer)
      this.openWSForPrinter(printer)
    },

    reinsertPrinter(printer) {
      let index = this.printers.findIndex(p => p.id == printer.id)
      if (index < 0) {
        // FIXME any alert here?
        return
      }

      this.$set(this.printers, index, printer)
    },

    openWSForPrinter(printer) {
      let printerId = printer.id
      const url = urls.printerWS(printer.id)
      this.printerWs.openPrinterWebSockets(
        printerId,
        url,
        (data) => {
          this.reinsertPrinter(normalizedPrinter(data))
        }
      )
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
