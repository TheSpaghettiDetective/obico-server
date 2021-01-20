<template>
  <div>
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
            :checked="!pauseAndNotify"
            @change="emitPauseAndNotify($event, false)">
          <label class="custom-control-label" for="id_action_on_failure_0">Just notify me</label>
        </div>
        <div class="custom-control custom-radio mt-1 input-wrapper radio" id="pauseAndNotifyTrue">
          <input
            type="radio"
            name="action_on_failure"
            class="custom-control-input field_required"
            id="id_action_on_failure_1"
            :checked="pauseAndNotify"
            @change="emitPauseAndNotify($event, true)">
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
                    :checked="isHotendHeaterOff"
                    @change="emitIsHotendHeaterOff($event)">
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
                    :checked="isBedHeaterOff"
                    @change="emitIsBedHeaterOff($event)">
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
                      :checked="retractFilamentBy !== false"
                      @change="emitRetractFilamentBy($event)">
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
                      v-model="retractFilamentByInput"
                      @change="EmitIfEtractFilamentBy($event)">
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
                      :checked="liftExtruderBy !== false"
                      @change="emitLiftExtruderBy($event)">
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
                      v-model="liftExtruderByInput"
                      @change="EmitIfLiftExtruderBy($event)">
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
                  <input id="sensitivity" name="detective_sensitivity" data-slider-id='sensitivity-slider' type="text"
                    data-slider-min="0.8" data-slider-max="1.2" data-slider-step="0.05" :data-slider-value="sensitivity" />
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
  </div>
</template>

<script>
import Slider from 'bootstrap-slider'

export default {
  name: 'PrinterPreferences',

  props: {
    pauseAndNotify: {
      type: Boolean,
      required: false,
      default: false
    },
    isHotendHeaterOff: {
      type: Boolean,
      required: false,
      default: false
    },
    isBedHeaterOff: {
      type: Boolean,
      required: false,
      default: false
    },
    retractFilamentBy: {
      type: [Boolean, String],
      required: false,
      default: false
    },
    liftExtruderBy: {
      type: [Boolean, String],
      required: false,
      default: false
    },
    sensitivity: {
      type: String,
      required: false,
      default: '1'
    }
  },

  data() {
    return {
      retractFilamentByInput: '0',
      liftExtruderByInput: '0',
      retractFilamentByTimeoutId: null, // Is used to make 1s pause before sending new value to API
      liftExtruderByTimeoutId: null // Is used to make 1s pause before sending new value to API
    }
  },

  methods: {
    /**
     * Clear loading indicator (useful in case of error)
     * @param {String} inputName
     * @param {any} value
     */
    clearAPICallAnimation: function(inputName, value) {
      const elem = this.getElementByName(inputName, value)
      if (elem) {
        elem.classList.remove('loading')
      }
    },

    /**
     * Show animation of successful settings save
     * @param {String} inputName
     * @param {any} value
     */
    successfullySavedFeedback: function(inputName, value) {
      const elem = this.getElementByName(inputName, value)

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
     * Emit input change to parent block
     */

    emitPauseAndNotify: function(event, value) {
      event.target.closest('.input-wrapper').classList.add('loading')
      this.$emit('pauseAndNotifyChanged', value)
    },

    emitIsHotendHeaterOff: function(event) {
      event.target.closest('.input-wrapper').classList.add('loading')
      this.$emit('isHotendHeaterOffChanged', event.target.checked)
    },
    emitIsBedHeaterOff: function(event) {
      event.target.closest('.input-wrapper').classList.add('loading')
      this.$emit('isBedHeaterOffChanged', event.target.checked)
    },

    emitRetractFilamentBy: function(event) {
      event.target.closest('.input-wrapper').classList.add('loading')

      if (event.target.checked) {
        this.$emit('retractFilamentByChanged', this.retractFilamentByInput)
      } else {
        this.$emit('retractFilamentByChanged', false)
      }
    },
    EmitIfEtractFilamentBy: function(event) {
      if (this.retractFilamentBy !== false) {
        if (this.retractFilamentByTimeoutId) {
          clearTimeout(this.retractFilamentByTimeoutId)
        }

        this.retractFilamentByTimeoutId = setTimeout(() => {
          event.target.closest('.input-wrapper').classList.add('loading')
          this.$emit('retractFilamentByChanged', this.retractFilamentByInput)
        }, 1000)
      }
    },

    emitLiftExtruderBy: function(event) {
      event.target.closest('.input-wrapper').classList.add('loading')

      if (event.target.checked) {
        this.$emit('liftExtruderByChanged', this.liftExtruderByInput)
      } else {
        this.$emit('liftExtruderByChanged', false)
      }
    },
    EmitIfLiftExtruderBy: function(event) {
      if (this.liftExtruderBy !== false) {
        if (this.liftExtruderByTimeoutId) {
          clearTimeout(this.liftExtruderByTimeoutId)
        }

        this.liftExtruderByTimeoutId = setTimeout(() => {
          event.target.closest('.input-wrapper').classList.add('loading')
          this.$emit('liftExtruderByChanged', this.liftExtruderByInput)
        }, 1000)
      }
    },

    emitSensitivityChange: function(newValue) {
      document.querySelector('.input-wrapper.sensitivity-slider').classList.add('loading')
      this.$emit('sensitivityChanged', String(newValue))
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
     * Returns input element by gived name
     * @param {String} elementId
     * @returns {Object, null}
     */
    getElementByName: function(inputName, value) {
      switch (inputName) {
        case 'pauseAndNotify':
          return value ? document.querySelector('#pauseAndNotifyTrue'): document.querySelector('#pauseAndNotifyFalse')
        case 'isHotendHeaterOff':
          return document.querySelector('#isHotendHeaterOff')
        case 'isBedHeaterOff':
          return document.querySelector('#isBedHeaterOff')
        case 'retractFilamentBy':
          return document.querySelector('#retractFilamentBy')
        case 'liftExtruderBy':
          return document.querySelector('#liftExtruderBy')
        case 'sensitivity':
          return document.querySelector('#sensitivityInputWrapper')
        default:
          return null
      }
    },
  },

  mounted() {
    // Put values into inputs (placed near checkboxes)
    if (this.retractFilamentBy !== false) {
      this.retractFilamentByInput = this.retractFilamentBy
    }
    if (this.liftExtruderBy !== false) {
      this.liftExtruderByInput = this.liftExtruderBy
    }

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

    sensitivitySlider.on('slideStop', this.emitSensitivityChange) // Emit new value to parent component
    sensitivitySlider.on('change', this.updateSensitivityHint) // Update hint depending of selected value
    this.updateSensitivityHint() // Initial hits update (hide all except one)
  },
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.form-label
  font-size: 18px

.card
  overflow: visible

.custom-control-label
  font-size: 16px

.input-group.minimal-width input
  width: 4rem

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
    top: 2px
    right: 0
    margin: auto
    z-index: 9
  
  &.sensitivity-slider:before
    right: -#{$indicatorSize + 16px}
  
  &.loading
    position: relative

    &:before
      background-image: url('/static/img/tail-spin.svg')

  &.successfully-saved
    position: relative
    
    &:before
      background-image: url('/static/img/tick.svg')
</style>
