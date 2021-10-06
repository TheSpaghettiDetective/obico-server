<template>
  <layout>
    <template v-slot:content>
      <b-container>
        <b-row class="justify-content-center">
          <b-col lg="8">
            <div v-if="printer" class="surface with-loading-animation full-on-mobile">
              <section class="settings">
                <h2 class="section-title">Settings</h2>
                <div class="form-group mb-4 mt-4">
                  <div class="form-label text-muted mb-2">Give your shiny new printer a name</div>
                  <saving-animation :errors="errorMessages.name" :saving="saving.name">
                    <input
                      id="id_name"
                      type="text"
                      name="name"
                      maxlength="200"
                      placeholder=""
                      class="form-control field_required"
                      required="required"
                      v-model="printer.name"
                    >
                  </saving-animation>
                </div>
                <!-- Potential failure section -->
                <div class="failure-notification">
                  <div class="form-group mt-4 mb-4">
                    <div class="form-label text-muted">When a potential failure is detected:</div>
                    <saving-animation :errors="errorMessages.action_on_failure_NONE" :saving="saving.action_on_failure_NONE">
                      <div class="custom-control custom-radio mt-1 radio">
                        <input
                          type="radio"
                          name="action_on_failure"
                          class="custom-control-input field_required"
                          id="id_action_on_failure_0"
                          value="NONE"
                          v-model="printer.action_on_failure"
                          @change="updateSetting('action_on_failure')"
                        >
                        <label class="custom-control-label" for="id_action_on_failure_0">Just notify me</label>
                      </div>
                    </saving-animation>
                    <saving-animation :errors="errorMessages.action_on_failure_PAUSE" :saving="saving.action_on_failure_PAUSE">
                      <div class="custom-control custom-radio mt-1 radio" id="action_on_failure_PAUSE">
                        <input
                          type="radio"
                          name="action_on_failure"
                          class="custom-control-input field_required"
                          id="id_action_on_failure_1"
                          value="PAUSE"
                          v-model="printer.action_on_failure"
                          @change="updateSetting('action_on_failure')"
                        >
                        <label class="custom-control-label" for="id_action_on_failure_1">Pause the printer and notify me</label>
                      </div>
                    </saving-animation>
                  </div>
                </div>
              </section>
              <section class="mt-5">
                <h2 class="section-title">Failure Detection</h2>
                  <div class="card-body p-0 pt-3">
                    <p class="text-warning">
                      <i class="fas fa-exclamation-triangle"></i>
                      If you are not sure about the settings below, leave the default values to minimize surprises.
                    </p>

                    <!-- Advanced settngs: when printer is paused -->
                    <div class="form-group mt-4">
                      <div class="form-label text-muted">When print is paused,</div>
                      <saving-animation :errors="errorMessages.tools_off_on_pause" :saving="saving.tools_off_on_pause">
                        <div class="custom-control custom-checkbox mt-2 checkbox">
                          <input
                            type="checkbox"
                            name="tools_off_on_pause"
                            class="custom-control-input"
                            id="id_tools_off_on_pause"
                            v-model="printer.tools_off_on_pause"
                            @change="updateSetting('tools_off_on_pause')"
                          >
                          <label class="custom-control-label" for="id_tools_off_on_pause">
                            Turn off hotend heater(s)
                          </label>
                        </div>
                      </saving-animation>
                      <saving-animation :errors="errorMessages.bed_off_on_pause" :saving="saving.bed_off_on_pause">
                        <div class="custom-control custom-checkbox mt-2 checkbox">
                          <input
                            type="checkbox"
                            name="bed_off_on_pause"
                            class="custom-control-input"
                            id="id_bed_off_on_pause"
                            v-model="printer.bed_off_on_pause"
                            @change="updateSetting('bed_off_on_pause')"
                          >
                          <label class="custom-control-label" for="id_bed_off_on_pause">
                            Turn off bed heater
                          </label>
                        </div>
                      </saving-animation>

                      <saving-animation :errors="errorMessages.retract_on_pause" :saving="saving.retract_on_pause" class="mobile-full-width">
                        <div class="form-inline my-1 checkbox-with-input">
                          <div class="custom-control custom-checkbox">
                            <input type="checkbox" class="custom-control-input" id="retract-checkbox" v-model="retractFilamentByEnabled">
                            <label class="custom-control-label" for="retract-checkbox">Retract filament by</label>
                          </div>
                          <number-input
                            v-model="retractOnPause"
                            :step=".5"
                            :disable="!retractFilamentByEnabled"
                            class="wrappable-field"
                          ></number-input>
                        </div>
                      </saving-animation>

                      <saving-animation :errors="errorMessages.lift_z_on_pause" :saving="saving.lift_z_on_pause" class="mobile-full-width">
                        <div class="form-inline my-1 checkbox-with-input">
                          <div class="custom-control custom-checkbox">
                            <input type="checkbox" class="custom-control-input" id="lift-z-checkbox" v-model="liftExtruderByEnabled">
                            <label class="custom-control-label" for="lift-z-checkbox">Lift extruder along Z axis by</label>
                          </div>
                          <number-input
                            v-model="liftExtruderBy"
                            :step=".5"
                            :disable="!liftExtruderByEnabled"
                            class="wrappable-field"
                          ></number-input>
                        </div>
                      </saving-animation>
                    </div>

                    <!-- Advanced settngs: sensitivity slider -->
                    <div class="form-group sensitivity my-4">
                      <div class="form-label text-muted">How sensitive do you want the Detective to be on this printer?</div>
                      <saving-animation :errors="errorMessages.detective_sensitivity" :saving="saving.detective_sensitivity">
                        <div class="my-2 sensitivity-slider">
                          <input
                            id="id_sensitivity"
                            name="detective_sensitivity"
                            data-slider-id='sensitivity-slider'
                            type="text"
                            data-slider-min="0.8"
                            data-slider-max="1.2"
                            data-slider-step="0.05"
                            :data-slider-value="printer.detective_sensitivity"
                          />
                        </div>
                      </saving-animation>
                      <div class="hint-low">
                        Low - I don't want a lot of false alarms. Only alert me when you are absolutely sure.
                      </div>
                      <div class="hint-medium">
                        Medium - A few false alarms won't bother me. But some well-disguised spaghetti will be missed.
                      </div>
                      <div class="hint-high">
                        High - Hit me with all the false alarms. I want to catch as many failures as possible.
                      </div>
                    </div>
                  </div>
              </section>
              <section class="mt-5">
                <h2 class="section-title">Time-lapse</h2>
                <p v-if="!(timelapseOnFinishEnabled && timelapseOnCancelEnabled)" class="text-warning">
                  <i class="fas fa-exclamation-triangle"></i>
                  Focused Feedback won't be available when time-lapse recording is turned off. You won't be able to <a href="https://www.thespaghettidetective.com/docs/how-does-credits-work/">help The Detective get better while earning Detective Hours for yourself</a>.
                </p>
                <div class="form-group mt-4">
                  <saving-animation :errors="errorMessages.min_timelapse_secs_on_finish" :saving="saving.min_timelapse_secs_on_finish" class="mobile-full-width">
                    <div class="form-inline my-1 checkbox-with-input">
                      <div class="custom-control custom-checkbox">
                        <input type="checkbox" class="custom-control-input" id="timelapseOnFinishEnabled" v-model="timelapseOnFinishEnabled">
                        <label class="custom-control-label" for="timelapseOnFinishEnabled">Record time-lapse when a print finishes successfully.</label>
                      </div>
                    </div>
                    <div
                      v-if="timelapseOnFinishEnabled"
                      class="form-inline my-1 checkbox-with-input"
                      >
                      <div class="custom-control custom-checkbox">
                        Skip if the print is finished in less than
                      </div>
                      <number-input
                        v-model="minTimelapseMinutesOnFinish"
                        :step="5"
                        unit="minutes"
                        class="wrappable-field"
                      ></number-input>
                    </div>
                  </saving-animation>
                  <saving-animation :errors="errorMessages.min_timelapse_secs_on_cancel" :saving="saving.min_timelapse_secs_on_cancel" class="mobile-full-width">
                    <div class="form-inline mt-3 mb-1 checkbox-with-input">
                      <div class="custom-control custom-checkbox">
                        <input type="checkbox" class="custom-control-input" id="timelapseOnCancelEnabled" v-model="timelapseOnCancelEnabled">
                        <label class="custom-control-label" for="timelapseOnCancelEnabled">Record time-lapse when a print is cancelled.</label>
                      </div>
                    </div>
                    <div
                      v-if="timelapseOnCancelEnabled"
                      class="form-inline my-1 checkbox-with-input"
                      >
                      <div class="custom-control custom-checkbox">
                        Skip if the print is cancelled in less than
                      </div>
                      <number-input
                        v-model="minTimelapseMinutesOnCancel"
                        :step="5"
                        unit="minutes"
                        class="wrappable-field"
                      ></number-input>
                    </div>
                  </saving-animation>
                </div>
              </section>
              <section class="danger mt-5">
                <h2 class="section-title">Danger Zone</h2>
                <div class="mt-4">
                  <a
                    class="btn btn-outline-secondary"
                    :href="printerWizardUrl">
                        Re-Link OctoPrint
                  </a>
                  <div class="text-muted mt-1">
                    <small>If your OctoPrint is always showing as "offline", and you have gone through <a href="https://www.thespaghettidetective.com/docs/octoprint-is-offline/">all the trouble-shooting steps</a>, you can try to re-link OctoPrint as the last resort.</small>
                  </div>
                </div>
                <div class="mt-4">
                  <button
                    class="btn btn-outline-danger"
                    @click="deletePrinter"
                  >
                    Delete Printer
                  </button>
                  <div class="text-muted mt-1">
                    <small>Bye-bye printer. See you next time!</small>
                  </div>
                </div>
              </section>
            </div>
            <div v-else class="text-center">
              <b-spinner class="mt-5" label="Loading..."></b-spinner>
            </div>
          </b-col>
        </b-row>
      </b-container>


      <!-- <div class="row justify-content-center">
        <div class="col-sm-11 col-md-10 col-lg-8">


        </div>
      </div> -->
    </template>
  </layout>
</template>

<script>
import axios from 'axios'
import split from 'lodash/split'
import Slider from 'bootstrap-slider'
import 'bootstrap-slider/dist/css/bootstrap-slider.css'

import { normalizedPrinter } from '@lib/normalizers'
import urls from '@lib/server_urls'
import SavingAnimation from '../common/SavingAnimation.vue'
import NumberInput from '../common/NumberInput.vue'
import Layout from '@common/Layout.vue'

export default {
  components: {
    SavingAnimation,
    NumberInput,
    Layout,
  },

  data() {
    return {
      printer: null,
      printerId: '',
      saving: {},
      errorMessages: {},
      delayedSubmit: { // Make pause before sending new value to API
        'name': {
          'delay': 1000,
          'timeoutId': null
        },
        'retract_on_pause': {
          'delay': 1000,
          'timeoutId': null
        },
        'lift_z_on_pause': {
          'delay': 1000,
          'timeoutId': null
        },
        'min_timelapse_secs_on_finish': {
          'delay': 1000,
          'timeoutId': null
        },
        'min_timelapse_secs_on_cancel': {
          'delay': 1000,
          'timeoutId': null
        },
      }
    }
  },

  computed: {
    retractFilamentByEnabled: {
      get(){
        return this.printer.retract_on_pause > 0
      },
      set(newValue){
        if (newValue) {
          this.printer.retract_on_pause = 6.5 // Default retraction value
        } else {
          this.printer.retract_on_pause = 0
        }
      },
    },
    retractOnPause: {
      get() {
        return this.printer ? this.printer.retract_on_pause : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.retract_on_pause = newValue
        }
      }
    },
    liftExtruderByEnabled: {
      get(){
        return this.printer.lift_z_on_pause > 0
      },
      set(newValue){
        if (newValue) {
          this.printer.lift_z_on_pause = 2.5 // Default z-lift value
        } else {
          this.printer.lift_z_on_pause = 0
        }
      },
    },
    liftExtruderBy: {
      get() {
        return this.printer ? this.printer.lift_z_on_pause : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.lift_z_on_pause = newValue
        }
      }
    },
    timelapseOnFinishEnabled: {
      get(){
        return this.printer.min_timelapse_secs_on_finish >= 0
      },
      set(newValue){
        if (newValue) {
          this.printer.min_timelapse_secs_on_finish = 600
        } else {
          this.printer.min_timelapse_secs_on_finish = -1
        }
      },
    },
    minTimelapseMinutesOnFinish: {
      get() {
        return this.printer ? this.printer.min_timelapse_secs_on_finish / 60 : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.min_timelapse_secs_on_finish = newValue * 60
        }
      }
    },
    timelapseOnCancelEnabled: {
      get(){
        return this.printer.min_timelapse_secs_on_cancel >= 0
      },
      set(newValue){
        if (newValue) {
          this.printer.min_timelapse_secs_on_cancel = 300
        } else {
          this.printer.min_timelapse_secs_on_cancel = -1
        }
      },
    },
    minTimelapseMinutesOnCancel: {
      get() {
        return this.printer ? this.printer.min_timelapse_secs_on_cancel / 60 : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.min_timelapse_secs_on_cancel = newValue * 60
        }
      }
    },
    printerWizardUrl() {
      return urls.printerWizard(this.printer.id)
    },

    printerName: {
      get: function() {
        return this.printer ? this.printer.name : undefined
      },
      set: function(newValue) {
        this.printer.name = newValue
      }
    },
  },

  // Watch these properties so that updates can be triggered at key-press, instead of losing focus
  // To watch deep properties in an object: https://stackoverflow.com/questions/42133894/vue-js-how-to-properly-watch-for-nested-data
  watch: {
    printerName: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('name')
      }
    },
    retractOnPause: function(newValue, oldValue) {
      if (oldValue !== undefined) {
        this.changeRetractOnPause(newValue)
      }
    },
    liftExtruderBy: function(newValue, oldValue) {
      if (oldValue !== undefined) {
        this.changeLiftExtruderBy(newValue)
      }
    },
    minTimelapseMinutesOnFinish: function(newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('min_timelapse_secs_on_finish')
      }
    },
    minTimelapseMinutesOnCancel: function(newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('min_timelapse_secs_on_cancel')
      }
    },
  },

  created() {
    this.printerId = split(window.location.pathname, '/').slice(-2, -1).pop()
    this.fetchPrinter().then(() => {
      // Instantiate sensitivity slider
      const sensitivitySlider = new Slider('#id_sensitivity', {
        formatter: function(value) {
          if (value < 0.95) {
            return 'Low'
          }
          if (value > 1.05) {
            return 'High'
          }
          return 'Medium'
        }
      })

      sensitivitySlider.on('slideStop', this.saveSensitivity) // Emit new value to parent component
      sensitivitySlider.on('change', this.updateSensitivityHint) // Update hint depending of selected value
      this.updateSensitivityHint() // Initial hits update (hide all except one)
    })
  },

  methods: {
    /**
     * Get actual printer settings
     */
    fetchPrinter() {
      return axios
        .get(urls.printer(this.printerId))
        .then(response => {
          this.printer = normalizedPrinter(response.data, this.printer)
        })
    },

    /**
     * Update printer settings
     * @param {String} propName
     * @param {any} propValue
     * @param {String} settingsItem
     */
    patchPrinter(propName, propValue) {

      const inputElem = this.getSettingsItemInput(propName, propValue)
      this.setSavingStatus(inputElem, true)

      // Make request to API
      return axios
        .patch(urls.printer(this.printerId), {
          [propName]: propValue
        })
        .catch(err => {
          if (err.response && err.response.data && typeof err.response.data === 'object') {
            if (err.response.data.non_field_errors) {
              this.errorAlert(err.response.data.non_field_errors)
            } else {
              for (const error in err.response.data) {
                this.errorMessages[inputElem] = err.response.data[error]
              }
            }
          } else {
            this.errorAlert()
          }
        })
        .then(() => {
          this.setSavingStatus(inputElem, false)
        })
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert() {
      this.$swal.Toast.fire({
        icon: 'error',
        html: '<div>Can not update printer settings.</div><div>Get help from <a href="https://discord.com/invite/NcZkQfj">TSD discussion forum</a> if this error persists.</div>',
      })
    },

    /**
     * Update particular settings item
     * @param {String} settingsItem
     */
    updateSetting(settingsItem) {
      if (settingsItem in this.delayedSubmit) {
        const delayInfo = this.delayedSubmit[settingsItem]
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }
        this.delayedSubmit[settingsItem]['timeoutId'] = setTimeout(() => {
          this.patchPrinter(settingsItem, this.printer[settingsItem])
        }, delayInfo['delay'])
        return
      }

      this.patchPrinter(settingsItem, this.printer[settingsItem])
    },

    /**
     * Callback for sensitivity slider
     * @param {String} newValue
     */
    saveSensitivity(newValue) {
      this.printer.detective_sensitivity = newValue
      this.updateSetting('detective_sensitivity')
    },

    /**
     * Update hint under sensitivity slider
     */
    updateSensitivityHint: function() {
      // Hide all hints
      const hints = document.querySelectorAll('.sensitivity div[class^=hint]');
      [].forEach.call(hints, function(hint) {
        hint.style.display = 'none'
      })

      // Show target hint depending of selected value
      var value = parseFloat(document.querySelector('#id_sensitivity').value)
      if (value < 0.95) {
        document.querySelector('.sensitivity .hint-low').style.display = 'block'
      } else if (value > 1.05) {
        document.querySelector('.sensitivity .hint-high').style.display = 'block'
      } else {
        document.querySelector('.sensitivity .hint-medium').style.display = 'block'
      }
    },

    /**
     * Confirm printer delete
     */
    deletePrinter() {
      this.$swal.Confirm.fire().then((result) => {
        if (result.value) {
          window.location.href = `/printers/${this.printerId}/delete/`
        }
      })
    },

    /**
     * Return input element by gived name
     * @param {String} settingsItem
     * @returns {Object, null}
     */
    getSettingsItemInput: function(settingsItem, value = '') {
      switch (settingsItem) {
        case 'action_on_failure':
          return `${settingsItem}_${value}`
        default:
          return `${settingsItem}`
      }
    },

    /**
     * Interlayer for saving status control to be able to set same saving status
     * for 2 or more different inputs grouped to one block
     * @param {String} propName
     * @param {String} status
     */
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },

    changeRetractOnPause(value) {
      this.printer.retract_on_pause = value
      this.updateSetting('retract_on_pause')
    },

    changeLiftExtruderBy(value) {
      this.printer.lift_z_on_pause = value
      this.updateSetting('lift_z_on_pause')
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.card
  overflow: visible !important

.custom-control-label
  font-size: 16px

@media (max-width: 768px)
  .mobile-full-width
    width: 100%
    margin-top: .25em
    margin-bottom: .4em

.section-title
  padding-bottom: 5px
  border-bottom: 1px solid var(--color-text-primary)

.form-label
  font-size: 18px

section.danger
  .section-title
    color: var(--color-danger)
    border-color: var(--color-danger)

.form-inline
  .wrappable-field
    padding-left: 1.5rem

</style>
