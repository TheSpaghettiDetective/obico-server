<template>
  <div :id="printer.id"
    class="col-sm-12 col-lg-6 printer-card"
  >
    <div class="card">
      <div class="card-header">
        <div class="title-box">
          <div
            v-if="hasCurrentPrintFilename"
            class="primary-title print-filename"
          >{{ printer.current_print.filename }}</div>
          <div
            class="printer-name"
            :class="{'secondary-title': hasCurrentPrintFilename}"
          >{{ printer.name }} &nbsp;
          (<a :href="'#printer-actions-' + printer.id" :class="statusClass">{{ statusText }}</a>)
          </div>
        </div>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item href="#" @click.prevent="onSharePrinter()">
            <i class="fas fa-share-alt fa-lg"></i>Share
          </b-dropdown-item>
          <b-dropdown-item :href="octoPrintTunnelUrl()">
            <svg class="menu-icon">
              <use href="#svg-octoprint-tunneling" />
            </svg>
            Tunneling
          </b-dropdown-item>
          <div class="dropdown-divider"></div>
          <b-dropdown-item :href="settingsUrl()">
            <i class="fas fa-wrench fa-lg"></i>Configure
          </b-dropdown-item>
        </b-dropdown>
      </div>
      <streaming-box :printer="printer" :webrtc="webrtc" />
      <div
        v-if="printer.alertUnacknowledged()"
        class="failure-alert card-body bg-warning px-2 py-1"
      >
        <i class="fas fa-exclamation-triangle align-middle"></i>
        <span class="align-middle">Failure Detected!</span>
        <button
          type="button"
          id="not-a-failure"
          class="btn btn-outline-primary btn-sm float-right"
          @click="onNotAFailureClicked($event, false)"
        >Not a failure?</button>
      </div>

      <div
        class="card-body gauge-container"
        :class="{overlay: !isWatching}"
      >
        <div
          v-if="!isWatching"
          class="overlay-top text-center"
          style="left: 0; width: 100%; top: 50%; margin-top: -55px;"
        >
          <H1><i class="far fa-eye-slash"></i></H1>
          <h5 class="text-warning">Failure Detection is Off</h5>
          <small
            v-if="printer.not_watching_reason"
          >{{ printer.not_watching_reason }}. <a href="https://www.obico.io/docs/user-guides/detective-not-watching/" target="_blank">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a></small>
          <div></div>
        </div>
        <Gauge
          :normalizedP="printer.normalized_p"
          :isWatching="isWatching"
        />
        <hr />
      </div>
      <PrinterActions
        :id="'printer-actions-' + printer.id"
        class="container"
        v-bind="actionsProps"
        @PrinterActionPauseClicked="onPrinterActionPauseClicked"
        @PrinterActionResumeClicked="onPrinterActionResumeClicked($event)"
        @PrinterActionCancelClicked="onPrinterActionCancelClicked"
        @PrinterActionConnectClicked="onPrinterActionConnectClicked"
        @PrinterActionStartClicked="onPrinterActionStartClicked"
        @PrinterActionControlClicked="onPrinterActionControlClicked"
      ></PrinterActions>
      <div class="info-section settings">
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.settings}"
          @click="onSettingsToggleClicked()"
        ><i class="fas fa-cog fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.time}"
          @click="onTimeToggleClicked()"
        ><i class="fas fa-clock fa-lg"></i></button>
        <button
          type="button"
          class="info-section-toggle btn btn-sm no-corner mx-2"
          :class="{pressed: section_toggles.statusTemp}"
          @click="onStatusTempToggleClicked()"
          ><i class="fas fa-thermometer-half fa-lg"></i></button>
      </div>
      <div class="info-section" style="height: 0.3rem;"></div>
      <div>
        <div class="info-section container">
          <div
            id="panel-settings"
            v-if="section_toggles.settings"
          >
            <div class="pt-2 pb-3">
              <div class="row justify-content-center px-3">
                <div class="col-12 setting-item">
                  <label
                    class="toggle-label"
                    :for="'watching_enabled-toggle-' + printer.id"
                  >Enable AI failure detection
                    <div
                      v-if="!watchForFailures"
                      class="text-muted font-weight-light font-size-sm">AI failure detection is disabled. You are on your own.
                    </div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input
                      type="checkbox"
                      name="watching_enabled"
                      class="custom-control-input update-printer"
                      :id="'watching_enabled-toggle-' + printer.id"
                      @click="onWatchForFailuresToggled"
                      :checked="watchForFailures"
                    >
                    <label
                      class="custom-control-label"
                      :for="'watching_enabled-toggle-' + printer.id"
                      style="font-size: 1rem;"
                    ></label>
                  </div>
                </div>
              </div>
              <div class="row justify-content-center px-3">
                <div class="col-12 setting-item">
                  <label
                    class="toggle-label"
                    :for="'pause-toggle-' + printer.id"
                  >Pause on detected failures
                    <div
                      v-if="!pauseOnFailure"
                      class="text-muted font-weight-light font-size-sm">You will still be alerted via notifications
                    </div>
                  </label>
                  <div class="custom-control custom-switch">
                    <input
                      type="checkbox"
                      name="pause_on_failure"
                      class="custom-control-input update-printer"
                      :id="'pause-toggle-' + printer.id"
                      @click="onPauseOnFailureToggled"
                      :checked="pauseOnFailure"
                    >
                    <label
                      class="custom-control-label"
                      :for="'pause-toggle-'+printer.id"
                      style="font-size: 1rem;">
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div
            v-if="section_toggles.time"
            id="print-time">
            <div class="py-2">
              <div class="row text-muted">
                <small class="col-5 offset-2">
                  Remaining
                </small>
                <small class="col-5">
                  Total
                </small>
              </div>
              <div class="row">
                <div class="col-2 text-muted">
                  <i class="fas fa-clock"></i>
                </div>
                <duration-block
                  id="print-time-remaining"
                  class="col-5 numbers"
                  v-bind="timeRemaining"
                ></duration-block>
                <duration-block
                  id="print-time-total"
                  class="col-5 numbers"
                  v-bind="timeTotal"
                ></duration-block>
                <div class="col-12">
                  <div class="progress" style="height: 2px;">
                    <div
                      id="print-progress"
                      class="progress-bar"
                      :class="{'progress-bar-striped': progressPct < 100, 'progress-bar-animated': progressPct < 100}"
                      role="progressbar"
                      aria-valuenow="0"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :style="`width: ${progressPct}%;`">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <StatusTemp
            v-if="section_toggles.statusTemp && tempProps.show"
            id="status_temp_block"
            v-bind="tempProps"
            @TempEditClicked="onTempEditClicked"
          ></StatusTemp>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'
import capitalize from 'lodash/capitalize'
import moment from 'moment'
import filter from 'lodash/filter'
import axios from 'axios'

import urls from '@config/server-urls'
import { normalizedPrinter, normalizedGcode } from '@src/lib/normalizers'
import PrinterComm from '@src/lib/printer_comm'
import WebRTCConnection from '@src/lib/webrtc'
import Gauge from '@src/components/Gauge'
import StreamingBox from '@src/components/StreamingBox'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import DurationBlock from './DurationBlock.vue'
import PrinterActions from './PrinterActions.vue'
import StatusTemp from './StatusTemp.vue'
import StartPrint from './StartPrint.vue'
import ConnectPrinter from './ConnectPrinter.vue'
import TempTargetEditor from './TempTargetEditor.vue'
import SharePrinter from './SharePrinter.vue'

const PAUSE_PRINT = '/pause_print/'
const RESUME_PRINT = '/resume_print/'
const CANCEL_PRINT = '/cancel_print/'
const MUTE_CURRENT_PRINT = '/mute_current_print/?mute_alert=true'
const ACK_ALERT_NOT_FAILED = '/acknowledge_alert/?alert_overwrite=NOT_FAILED'

const Show = true
const Hide = false

const LocalPrefNames = {
  Settings: 'panel-settings',
  Time: 'print-time',
  StatusTemp: 'status_temp_block',
}

export default {
  name: 'PrinterCard',
  components: {
    StreamingBox,
    Gauge,
    DurationBlock,
    PrinterActions,
    StatusTemp,
  },

  props: {
    printer: {
      type: Object,
      required: true
    },
    isProAccount: {
      type: Boolean,
      required: true
    },
  },
  data() {
    return {
      section_toggles: {
        settings: getLocalPref(LocalPrefNames.Settings + String(this.printer.id), Show),
        time: getLocalPref(LocalPrefNames.Time + String(this.printer.id), Hide),
        statusTemp: getLocalPref(LocalPrefNames.StatusTemp + String(this.printer.id), Show),
      },
      webrtc: WebRTCConnection(this.isProAccount),
    }
  },
  created() {
    this.printerComm = PrinterComm(
      this.printer.id,
      urls.printerWebSocket(this.printer.id),
      (data) => {
        this.$emit('PrinterUpdated', this.updatedPrinter(data))
      },
      (printerStatus) => {
        this.$emit('PrinterUpdated', this.updatedPrinter(
          {status: printerStatus.octoprint_data}))
      }
    )
    this.printerComm.connect()

    this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
    this.printerComm.setWebRTC(this.webrtc)
  },
  computed: {
    isWatching() {
      return !this.printer.not_watching_reason
    },
    timeRemaining() {
      return this.toDuration(
        this.secondsLeft, this.printer.isPrinting())
    },
    timeTotal() {
      let secs = null
      if (this.secondsPrinted && this.secondsLeft) {
        secs = this.secondsPrinted + this.secondsLeft
      }
      return this.toDuration(
        secs,
        this.printer.isPrinting())
    },
    secondsLeft() {
      return get(this.printer, 'status.progress.printTimeLeft')
    },
    secondsPrinted() {
      return get(this.printer, 'status.progress.printTime')
    },
    watchForFailures() {
      return this.printer.watching_enabled
    },
    pauseOnFailure() {
      return this.printer.action_on_failure == 'PAUSE'
    },
    hasCurrentPrintFilename() {
      if (this.printer.current_print && this.printer.current_print.filename) {
        return true
      }
      return false
    },
    actionsProps() {
      return {
        printer: this.printer,
      }
    },
    progressPct() {
      return get(this.printer, 'status.progress.completion') || 0 // get(this.printer, 'status.progress.completion') may return null
    },
    tempProps() {
      // If temp_profiles is missing, it's a plugin version too old to change temps
      let editable = get(this.printer, 'settings.temp_profiles') != undefined
      let temperatures = []
      const keys = ['bed', 'tool0', 'tool1']
      keys.forEach((tempKey) => {
        let temp = get(this.printer, 'status.temperatures.' + tempKey)
        if (temp) {
          temp.actual = parseFloat(temp.actual).toFixed(1)
          temp.target = Math.round(temp.target)
          Object.assign(temp, {toolName: capitalize(tempKey)})
          temp.id = this.printer.id + '-' + tempKey
          temp.key = tempKey
          temperatures.push(temp)
        }
      })
      return {
        temperatures: temperatures,
        show: temperatures.length > 0,
        editable: editable,
      }
    },
    statusText() {
      return get(this.printer, 'status.state.text', 'Offline')
    },
    statusClass() {
      if (this.printer.hasError()) {
        return 'text-danger'
      }
      if (this.printer.isOffline() || this.printer.isDisconnected() || this.printer.inTransientState()) {
        return 'text-warning'
      }
      return 'text-success'
    }
  },

  methods: {
    updatedPrinter(newData) {
      return normalizedPrinter(newData, this.printer)
    },
    settingsUrl() {
      return `/printers/${this.printer.id}/`
    },
    octoPrintTunnelUrl() {
      return `/tunnels/${this.printer.id}/`
    },
    onSettingsToggleClicked() {
      this.section_toggles.settings = !this.section_toggles.settings
      setLocalPref(LocalPrefNames.Settings + String(this.printer.id), this.section_toggles.settings)
    },
    onTimeToggleClicked() {
      this.section_toggles.time = !this.section_toggles.time
      setLocalPref(LocalPrefNames.Time + String(this.printer.id), this.section_toggles.time)
    },
    onStatusTempToggleClicked() {
      this.section_toggles.statusTemp = !this.section_toggles.statusTemp
      setLocalPref(LocalPrefNames.StatusTemp + String(this.printer.id), this.section_toggles.statusTemp)
    },
    onNotAFailureClicked(ev, resumePrint) {
      this.$swal.Confirm.fire({
        title: 'Noted!',
        html: '<p>Do you want to keep failure detection on for this print?</p><small>If you select "No", failure detection will be turned off for this print, but will be automatically turned on for your next print.</small>',
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
      }).then((result) => {
        if (result.dismiss == 'cancel') {
          // Hack: So that 2 APIs are not called at the same time
          setTimeout(() => {
            this.sendPrinterAction(
              this.printer.id,
              MUTE_CURRENT_PRINT,
              false
            )
          }, 1000)
        }
        if (resumePrint) {
          this.sendPrinterAction(
            this.printer.id,
            RESUME_PRINT,
            true)
        } else {
          this.sendPrinterAction(
            this.printer.id,
            ACK_ALERT_NOT_FAILED,
            false)
        }
      })

      ev.preventDefault()
    },
    onWatchForFailuresToggled() {
      this.printer.watching_enabled = !this.printer.watching_enabled
      this.updatePrinter(this.printer)
    },
    onPauseOnFailureToggled() {
      this.printer.action_on_failure = this.printer.action_on_failure == 'PAUSE' ? 'NONE' : 'PAUSE'
      this.updatePrinter(this.printer)
    },
    onPrinterActionPauseClicked() {
      this.$swal.Confirm.fire({
        html: 'If you haven\'t changed the default configuration, the heaters will be turned off, and the print head will be z-lifted. The reversed will be performed before the print is resumed. <a target="_blank" href="https://www.obico.io/docs/user-guides/detection-print-job-settings#when-print-is-paused">Learn more. <small><i class="fas fa-external-link-alt"></i></small></a>',
      }).then((result) => {
        if (result.value) {
          this.sendPrinterAction(this.printer.id, PAUSE_PRINT, true)
        }
      })
    },
    onPrinterActionResumeClicked(ev) {
      if (this.printer.alertUnacknowledged()) {
        this.onNotAFailureClicked(ev, true)
      } else {
        this.sendPrinterAction(this.printer.id, RESUME_PRINT, true)
      }
    },
    onPrinterActionCancelClicked() {
      this.$swal.Confirm.fire({
        text: 'Once cancelled, the print can no longer be resumed.',
      }).then((result) => {
        if (result.value) {
          // When it is confirmed
          this.sendPrinterAction(this.printer.id, CANCEL_PRINT, true)
        }
      })
    },
    onPrinterActionConnectClicked() {
      this.printerComm.passThruToPrinter(
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
                  this.printerComm.passThruToPrinter(
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
    onPrinterActionStartClicked() {
      if (!this.isProAccount) {
        this.$swal.Reject.fire({
          html: `
              <h5 class="mb-3">You need to <a href="/ent_pub/pricing/">upgrade to Pro plan</a> to start a remote print job. </h5>
              <p>Remote G-Code upload and print start is a Pro feature.</p>
              <p>With <a href="/ent_pub/pricing/">little more than 1 Starbucks per month</a>, you can upgrade to a Pro account.</p>
            `
        })
        return
      }

      axios
        .get(
          urls.gcodes(1, 1000),
        ).then((response) => {
          let gcodeFiles = [...response.data.results.map(gcode => normalizedGcode(gcode))]

          this.$swal.openModalWithComponent(
            StartPrint,
            {
              gcodeFiles: gcodeFiles,
              onGcodeFileSelected: this.onGcodeFileSelected,
            },
            {
              title: 'Start print on "' + this.printer.name + '"',
              showConfirmButton: false,
              showCloseButton: true,
            }
          )
        })
    },
    onGcodeFileSelected(gcodeFiles, gcodeFileId) {
      // actionsDiv.find('button').attr('disabled', true) // TODO

      this.printerComm.passThruToPrinter(
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
              Uploading G-Code to ${this.printer.name} ...
            </h5>
            <p>
              ${targetPath}
            </p>
          </div>`

          this.$swal.Prompt.fire({
            html: html,
            showConfirmButton: false
          })

          let checkPrinterStatus = () => {
            if (get(this.printer, 'status.state.text') == 'Operational') {
              setTimeout(checkPrinterStatus, 1000)
            } else {
              this.$swal.close()
            }
          }
          checkPrinterStatus()
        }
      )
    },

    onPrinterActionControlClicked() {
      window.location = urls.printerControl(this.printer.id)
    },

    onTempEditClicked(item) {
      let tempProfiles = get(this.printer, 'settings.temp_profiles', [])
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
          this.printerComm.passThruToPrinter(
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
          if (response.data.succeeded) {
            this.$emit('PrinterUpdated', normalizedPrinter(response.data.printer, this.printer))
          } else {
            throw response
          }
        })
        .catch(response => {
          console.error(response)
          this.$swal.Toast.fire({
            icon: 'error',
            title: 'Failed to update printer!',
          }) // FIXME this was not handled in original code. sentry?
        })
    },

    sendPrinterAction(printerId, path, isOctoPrintCommand) {
      axios
        .post(urls.printerAction(printerId, path))
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
      let shouldBeThumb = printer.alertUnacknowledged() && hasImage
      return !shouldBeThumb
    },

    toDuration (seconds, isPrinting) {
      if (seconds == null || seconds == 0) {
        return {
          valid: false,
          printing: isPrinting,
        }
      } else {
        var d = moment.duration(seconds, 'seconds')
        var h = Math.floor(d.asHours())
        var m = d.minutes()
        var s = d.seconds()
        return {
          valid: true,
          printing: isPrinting,
          hours: h,
          showHours: (h>0),
          minutes: m,
          showMinutes: (h>0 || m>0),
          seconds: s,
          showSeconds: (h==0 && m==0)
        }
      }
    },

    onSharePrinter() {
      this.$swal.openModalWithComponent(
        SharePrinter,
        {
          isProAccount: this.isProAccount,
          printer: this.printer
        },
        {
          confirmButtonText: 'Close',
        }
      )
    }
  },
}
</script>

<style lang="sass" scoped>
.menu-icon
  width: 20px
  height: 20px
  margin-right: 6px
</style>
