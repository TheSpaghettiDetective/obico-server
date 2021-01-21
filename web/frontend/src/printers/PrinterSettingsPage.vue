<template>
<div class="row justify-content-center">
  <div class="col-sm-12 col-md-10 col-lg-8 settings-container">
    <section class="settings">
      <h2 class="section-title">Settings</h2>
      <div class="form-group mb-4 mt-4">
        <div class="form-label text-muted mb-2">Give your shiny new printer a name</div>
        <form @submit.prevent="updateSetting('printerName')" id="printerNameForm" class="input-wrapper">
          <input
            id="printerName"
            type="text"
            name="name"
            v-model="printerName"
            maxlength="200"
            placeholder="My Awesome 3D Printer"
            class="form-control field_required"
            required="required"
          >
            <small class="text-muted">Click Enter to save new name</small>
        </form>
      </div>

      <!-- Potential failure section -->
      <div class="failure-notification">
        <div class="form-group mt-4 mb-4">
          <div class="form-label text-muted">When a potential failure is detected:</div>
          <div class="custom-control custom-radio mt-1 input-wrapper radio" id="pauseAndNotifyFalse">
            <input
              type="radio"
              name="action_on_failure"
              class="custom-control-input field_required"
              id="id_action_on_failure_0"
              value="NONE"
              v-model="actionOnFailure"
              @change="updateSetting('actionOnFailure')"
            >
            <label class="custom-control-label" for="id_action_on_failure_0">Just notify me</label>
          </div>
          <div class="custom-control custom-radio mt-1 input-wrapper radio" id="pauseAndNotifyTrue">
            <input
              type="radio"
              name="action_on_failure"
              class="custom-control-input field_required"
              id="id_action_on_failure_1"
              value="PAUSE"
              v-model="actionOnFailure"
              @change="updateSetting('actionOnFailure')"
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
                  <div class="custom-control custom-checkbox form-check-inline mt-2 input-wrapper checkbox" id="isHotendHeaterOff">
                    <input
                      type="checkbox"
                      name="tools_off_on_pause"
                      class="custom-control-input"
                      id="id_tools_off_on_pause"
                      v-model="advancedSettings.isHotendHeaterOff"
                      @change="updateSetting('isHotendHeaterOff')"
                    >
                    <label class="custom-control-label" for="id_tools_off_on_pause">
                      Turn off hotend heater(s)
                    </label>
                  </div>
                  <div class="custom-control custom-checkbox form-check-inline mt-2 input-wrapper checkbox" id="isBedHeaterOff">
                    <input
                      type="checkbox"
                      name="bed_off_on_pause"
                      class="custom-control-input"
                      id="id_bed_off_on_pause"
                      v-model="advancedSettings.isBedHeaterOff"
                      @change="updateSetting('isBedHeaterOff')"
                    >
                    <label class="custom-control-label" for="id_bed_off_on_pause">
                      Turn off bed heater
                    </label>
                  </div>
                  <div class="form-inline my-1 input-wrapper checkbox-with-input" id="retractFilamentBy">
                    <div class="custom-control custom-checkbox form-check-inline">
                      <input
                        type="checkbox"
                        class="custom-control-input"
                        id="retract-checkbox"
                        v-model="advancedSettings.retractFilamentByEnabled"
                        @change="updateSetting('retractFilamentByEnabled')"
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
                        v-model="advancedSettings.retractFilamentBy"
                        @change="updateSetting('retractFilamentBy')"
                      >
                      <div class="input-group-append">
                        <span class="input-group-text">mm</span>
                      </div>
                    </div>
                  </div>
                  <div class="form-inline my-1 input-wrapper checkbox-with-input" id="liftExtruderBy">
                    <div class="custom-control custom-checkbox form-check-inline">
                      <input
                        type="checkbox"
                        class="custom-control-input"
                        id="lift-z-checkbox"
                        v-model="advancedSettings.liftExtruderByEnabled"
                        @change="updateSetting('liftExtruderByEnabled')"
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
                        v-model="advancedSettings.liftExtruderBy"
                        @change="updateSetting('liftExtruderBy')"
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
                  <div class="my-2 input-wrapper sensitivity-slider" id="sensitivityInputWrapper">
                    <input
                      id="sensitivity"
                      name="detective_sensitivity"
                      data-slider-id='sensitivity-slider'
                      type="text"
                      data-slider-min="0.8"
                      data-slider-max="1.2"
                      data-slider-step="0.05"
                      :data-slider-value="advancedSettings.sensitivity"
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
</div>
</template>

<script>
import axios from 'axios'
import Slider from 'bootstrap-slider'

import { normalizedPrinter } from '@lib/normalizers'
import urls from '@lib/server_urls'

export default {
  components: {
  },

  data() {
    return {
      printer: null,
      printerId: '',
      loading: false,
      printerName: '',
      actionOnFailure: 'NONE', // NONE, PAUSE
      advancedSettings: {
        isHotendHeaterOff: true, // true, false
        isBedHeaterOff: false, // true, false

        retractFilamentByEnabled: false, // false or number (in string format) from 0 with 0.5 step
        liftExtruderByEnabled: true, // false or number (in string format) from 0 with 0.5 step
        retractFilamentBy: '0',
        liftExtruderBy: '0',
        retractFilamentByTimeoutId: null, // Is used to make 1s pause before sending new value to API
        liftExtruderByTimeoutId: null, // Is used to make 1s pause before sending new value to API

        sensitivity: '1', // number (in string format) from 0.8 to 1.2 with 0.05 step
      }
    }
  },

  mounted() {
    this.printerId = (new URLSearchParams(window.location.search)).get('printerId')
    this.fetchPrinter()

    // Instantiate sensitivity slider
    const sensitivitySlider = new Slider('#sensitivity', {
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
  },

  methods: {
    /**
     * Get actual printer settings
     */
    fetchPrinter() {
      this.loading = true
      return axios
        .get(urls.printer(this.printerId))
        .then(response => {
          this.loading = false
          this.printer = normalizedPrinter(response.data)

          this.printerName = this.printer.name
          this.actionOnFailure = this.printer.action_on_failure
          this.advancedSettings.isHotendHeaterOff = this.printer.tools_off_on_pause
          this.advancedSettings.isHotendHeaterOff = this.printer.bed_off_on_pause

          if (this.printer.retract_on_pause !== false) {
            this.advancedSettings.retractFilamentByEnabled = true
            this.advancedSettings.retractFilamentBy = this.printer.retract_on_pause
          } else {
            this.advancedSettings.retractFilamentByEnabled = false
          }

          if (this.printer.lift_z_on_pause !== false) {
            this.advancedSettings.liftExtruderByEnabled = true
            this.advancedSettings.liftExtruderBy = this.printer.lift_z_on_pause
          } else {
            this.advancedSettings.liftExtruderByEnabled = false
          }

          this.advancedSettings.sensitivity = this.printer.detective_sensitivity
        })
    },

    /**
     * Update printer settings
     * @param {String} propName
     * @param {any} propValue
     * @param {String} settingsItem
     */
    patchPrinter(propName, propValue, settingsItem) {
      // Find input element to set loading animation
      let inputElem = this.getSettingsItemInput(settingsItem)
      if (!inputElem) {
        this.errorAlert()
        console.log('Frontend error - can not find input element')
        return
      }
      inputElem.classList.add('loading')

      // Make request to API
      return axios
        .patch(urls.printer(this.printerId), {
          propName: propValue
        })
        .then(response => {
          // TODO: recognize success response
          console.log(response)
          this.successfullySavedFeedback(settingsItem)
        })
        .catch(err => {
          this.clearAPICallAnimation(settingsItem)
          this.errorAlert()
          console.log(err)
        })
    },

    /**
     * Show animation of successful settings save
     * @param {String} inputName
     * @param {any} value
     */
    successfullySavedFeedback: function(inputName, value = '') {
      const elem = this.getSettingsItemInput(inputName, value)

      if (elem) {
        elem.classList.remove('loading')
        elem.classList.add('successfully-saved')
        setTimeout(
          () => elem.classList.remove('successfully-saved'),
          800
        )
      }
    },

    /**
     * Clear loading indicator (used in case of error)
     * @param {String} inputName
     * @param {any} value
     */
    clearAPICallAnimation: function(inputName, value) {
      const elem = this.getSettingsItemInput(inputName, value)
      if (elem) {
        elem.classList.remove('loading')
      }
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert() {
      this.$swal('Error occured!', '<p class="text-center">Can not save your new settings, please try again.</p>', 'error')
    },


    /**
     * Update particular settings item
     * @param {String} settingsItem
     */
    updateSetting(settingsItem) {
      let propName = '', propValue = ''

      switch (settingsItem) {
        case 'printerName':
          propName = 'name'
          propValue = this.printerName

          if (!this.printerName) {
            return
          }

          break
        case 'actionOnFailure':
          propName = 'action_on_failure'
          propValue = this.actionOnFailure
          break
        case 'isHotendHeaterOff':
          propName = 'tools_off_on_pause'
          propValue = this.advancedSettings.isHotendHeaterOff
          break
        case 'isBedHeaterOff':
          propName = 'bed_off_on_pause'
          propValue = this.advancedSettings.isBedHeaterOff
          break

        case 'retractFilamentByEnabled':
          propName = 'retract_on_pause'

          if (this.advancedSettings.retractFilamentByEnabled) {
            propValue = this.advancedSettings.retractFilamentBy
          } else {
            propValue = false
          }
          break
        case 'retractFilamentBy':
          propName = 'retract_on_pause'
          propValue = this.advancedSettings.retractFilamentBy

          // Waiting final value from user
          if (this.advancedSettings.retractFilamentByTimeoutId) {
            clearTimeout(this.advancedSettings.retractFilamentByTimeoutId)
          }
          this.advancedSettings.retractFilamentByTimeoutId = setTimeout(() => {
            this.patchPrinter(propName, propValue, settingsItem)
          }, 1000)
          return

        case 'liftExtruderByEnabled':
          propName = 'lift_z_on_pause'

          if (this.advancedSettings.liftExtruderByEnabled) {
            propValue = this.advancedSettings.liftExtruderBy
          } else {
            propValue = false
          }
          break
        case 'liftExtruderBy':
          propName = 'lift_z_on_pause'
          propValue = this.advancedSettings.liftExtruderBy
          
          // Waiting final value from user
          if (this.advancedSettings.liftExtruderByTimeoutId) {
            clearTimeout(this.advancedSettings.liftExtruderByTimeoutId)
          }
          this.advancedSettings.liftExtruderByTimeoutId = setTimeout(() => {
            this.patchPrinter(propName, propValue, settingsItem)
          }, 1000)
          return

        case 'sensitivity':
          propName = 'detective_sensitivity'
          propValue = this.advancedSettings.sensitivity
          break
        default:
          return
      }

      this.patchPrinter(propName, propValue, settingsItem)
    },

    /**
     * Callback for sensitivity slider
     * @param {String} newValue
     */
    saveSensitivity(newValue) {
      this.advancedSettings.sensitivity = newValue
      this.updateSetting('sensitivity')
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
      var value = parseFloat(document.querySelector('#sensitivity').value)
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
          console.log('Delete printer')
          // TODO: delete printer
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
        case 'printerName':
          return document.querySelector('#printerNameForm')
        case 'actionOnFailure':
          return value ? document.querySelector('#pauseAndNotifyTrue'): document.querySelector('#pauseAndNotifyFalse')
        case 'isHotendHeaterOff':
          return document.querySelector('#isHotendHeaterOff')
        case 'isBedHeaterOff':
          return document.querySelector('#isBedHeaterOff')
        case 'retractFilamentBy':
          return document.querySelector('#retractFilamentBy')
        case 'retractFilamentByEnabled':
          return document.querySelector('#retractFilamentBy')
        case 'liftExtruderBy':
          return document.querySelector('#liftExtruderBy')
        case 'liftExtruderByEnabled':
          return document.querySelector('#liftExtruderBy')
        case 'sensitivity':
          return document.querySelector('#sensitivityInputWrapper')
        default:
          return
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

// API call animation
.input-wrapper
  $indicatorSize: 16px

  &:before
    content: ""
    background-size: $indicatorSize $indicatorSize
    width: $indicatorSize
    height: $indicatorSize
    display: block
    position: absolute
    top: 10px
    right: -#{$indicatorSize + 16px}
    margin: auto
    z-index: 9

  &.loading
    position: relative

    &:before
      background-image: url('/static/img/tail-spin.svg')

  &.successfully-saved
    position: relative

    &:before
      background-image: url('/static/img/tick.svg')
</style>
