<template>
<div class="row justify-content-center">
  <div v-if="printer" class="col-sm-12 col-md-10 col-lg-8 settings-container">
    <section class="settings">
      <h2 class="section-title">Settings</h2>
      <div class="form-group mb-4 mt-4">
        <div class="form-label text-muted mb-2">Give your shiny new printer a name</div>
        <div id="name">
          <input
            id="id_name"
            type="text"
            name="name"
            maxlength="200"
            placeholder=""
            class="form-control field_required"
            required="required"
            v-model="printer.name"
            @keyup="updateSetting('name')"
          >
        </div>
      </div>

      <!-- Potential failure section -->
      <div class="failure-notification">
        <div class="form-group mt-4 mb-4">
          <div class="form-label text-muted">When a potential failure is detected:</div>
          <div class="custom-control custom-radio mt-1 radio" id="action_on_failure_NONE">
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
        </div>
      </div>

      <!-- Advanced settings section (toggle) -->
      <div class="advanced">
        <div class="accordion">
          <div class="card" style="border: none;">
            <div class="card-header">
              <a class="card-link btn-block" data-toggle="collapse" href="#menuone" aria-expanded="false" aria-controls="menuone">
                Advanced Settings
                <span class="collapsed"><p><b>&gt;</b></p></span>
                <span class="expanded"><p><b>&lt;</b></p></span>
              </a>
            </div>
            <div id="menuone" class="collapse">
              <div class="card-body p-0 pt-3">
                <p class="text-warning">
                  <i class="fas fa-exclamation-triangle"></i>
                  If you are not sure about the settings below, leave the default values to minimize surprises.
                </p>

                <!-- Advanced settngs: when printer is paused -->
                <div class="form-group mt-4">
                  <div class="form-label text-muted">When print is paused,</div>
                  <div class="custom-control custom-checkbox form-check-inline mt-2 checkbox" id="tools_off_on_pause">
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
                  <div class="custom-control custom-checkbox form-check-inline mt-2 checkbox" id="bed_off_on_pause">
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
                  <div class="form-inline my-1 checkbox-with-input" id="retract_on_pause">
                    <div class="custom-control custom-checkbox form-check-inline">
                      <input
                        type="checkbox"
                        class="custom-control-input"
                        id="retract-checkbox"
                        v-model="retractFilamentByEnabled"
                        >
                      <label class="custom-control-label" for="retract-checkbox">Retract filament by</label>
                    </div>
                    <div class="input-group input-group-sm minimal-width">
                      <input
                        type="number"
                        name="retract_on_pause"
                        step="0.5"
                        aria-label="Retraction ammount in millimeters"
                        min="0"
                        class="form-control field_required"
                        id="id_retract_on_pause"
                        v-model="printer.retract_on_pause"
                        :disabled="!retractFilamentByEnabled"
                        @change="updateSetting('retract_on_pause')"
                      >
                      <div class="input-group-append">
                        <span class="input-group-text">mm</span>
                      </div>
                    </div>
                  </div>
                  <div class="form-inline my-1 checkbox-with-input" id="lift_z_on_pause">
                    <div class="custom-control custom-checkbox form-check-inline">
                      <input
                        type="checkbox"
                        class="custom-control-input"
                        id="lift-z-checkbox"
                        v-model="liftExtruderByEnabled"
                      >
                      <label class="custom-control-label" for="lift-z-checkbox">Lift extruder along Z axis by</label>
                    </div>
                    <div class="input-group input-group-sm minimal-width">
                      <input
                        type="number"
                        name="lift_z_on_pause"
                        step="0.5"
                        aria-label="Lift Z Axis ammount in millimeters"
                        min="0"
                        class="form-control field_required"
                        id="id_lift_z_on_pause"
                        :disabled="!liftExtruderByEnabled"
                        v-model="printer.lift_z_on_pause"
                        @change="updateSetting('lift_z_on_pause')"
                      >
                      <div class="input-group-append">
                        <span class="input-group-text">mm</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Advanced settngs: sensitivity slider -->
                <div class="form-group sensitivity my-4">
                  <div class="form-label text-muted">How sensitive do you want the Detective to be on this printer?</div>
                  <div class="my-2 sensitivity-slider" id="detective_sensitivity">
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
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="mt-5" v-if="extEndpointLength && extEndpointLength > 0">
      <h2 class="section-title">Integration</h2>
      <a role="button" type="button" class="btn btn-outline-primary my-2" :href="integrationUrl">{{ this.printer.service_token ? 'Change/Remove 3D Geeks push notification' : 'Set up 3D Geeks push notification' }}</a>
      <div class="mt-2">3D Geeks mobile app can be downloaded <a href="https://www.3dgeeks.app/u/tsd-android">here</a>.</div>
      <small class="text-muted font-italic">Disclaimer: 3D Geeks is not affiliated with The Spaghetti Detective.</small>
    </section>
    <section class="danger mt-5">
      <h2 class="section-title">Danger Zone</h2>
      <div class="text-center mt-4">
        <button
          class="btn btn-outline-danger"
          @click="deletePrinter"
        >
          Delete Printer
        </button>
      </div>
    </section>
  </div>
  <b-spinner v-else class="mt-5" label="Loading..."></b-spinner>
</div>
</template>

<script>
import axios from 'axios'
import Slider from 'bootstrap-slider'
import SavingLoader from '../common/SavingLoader'

import { normalizedPrinter } from '@lib/normalizers'
import urls from '@lib/server_urls'

export default {
  mixins: [SavingLoader],
  components: {
  },

  props: {
    extEndpointLength: {
      type: Number
    },
  },

  data() {
    return {
      printer: null,
      printerId: '',
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
        this.updateSetting('retract_on_pause')
      },
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
        this.updateSetting('lift_z_on_pause')
      },
    },
    integrationUrl() {
      return `/printers/${this.printerId}/integration/`
    },
  },

  mounted() {
    this.printerId = (new URLSearchParams(window.location.search)).get('printerId')
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
          this.printer = normalizedPrinter(response.data)
        })
    },

    /**
     * Update printer settings
     * @param {String} propName
     * @param {any} propValue
     * @param {String} settingsItem
     */
    patchPrinter(propName, propValue) {
      // Find input element to set loading animation
      let inputElem = this.getSettingsItemInput(propName, propValue)
      if (!inputElem) {
        this.errorAlert()
        console.log('Frontend error - can not find input element')
        return
      }
      
      this.savingInProgressFeedback(inputElem)

      // Make request to API
      return axios
        .patch(urls.printer(this.printerId), {
          [propName]: propValue
        })
        .then(() => {
          this.successfullySavedFeedback(inputElem)
        })
        .catch(err => {
          this.clearSavingLoader(inputElem)
          this.errorAlert()
          console.log(err)
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
          return document.querySelector(`#${settingsItem}_${value}`)
        default:
          return document.querySelector(`#${settingsItem}`)
      }
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.card
  overflow: visible !important

.custom-control-label
  font-size: 16px

.input-group.minimal-width input
  width: 4rem

.settings-container
  margin: 2em 0em
  padding: 2em 3em
  background: theme.$body-bg
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important

.section-title
  padding-bottom: 5px
  border-bottom: 1px solid theme.$white

.form-label
  font-size: 18px

section.danger
  .section-title
    color: theme.$danger
    border-color: theme.$danger
</style>
