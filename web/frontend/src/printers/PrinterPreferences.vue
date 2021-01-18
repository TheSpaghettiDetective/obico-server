<template>
  <div>
    <div class="failure-notification">
      <div class="form-group mt-4 mb-4">
        <div class="form-label text-muted">When a potential failure is detected:</div>
        <div class="custom-control custom-radio mt-1">
          <input type="radio" name="action_on_failure" value="NONE" class="custom-control-input field_required" required="" id="id_action_on_failure_0" checked="">
          <label class="custom-control-label" for="id_action_on_failure_0">Just notify me</label>
        </div>
        <div class="custom-control custom-radio mt-1">
          <input type="radio" name="action_on_failure" value="PAUSE" class="custom-control-input field_required" required="" id="id_action_on_failure_1">
          <label class="custom-control-label" for="id_action_on_failure_1">Pause the printer and notify me</label>
        </div>
      </div>
    </div>
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
              <div class="form-group mt-4">
                <div class="form-label text-muted">When print is paused,</div>
                <div class="custom-control custom-checkbox form-check-inline mt-2">
                  <input type="checkbox" name="tools_off_on_pause" class="custom-control-input" id="id_tools_off_on_pause" checked="">
                  <label class="custom-control-label" for="id_tools_off_on_pause">
                    Turn off hotend heater(s)
                  </label>
                </div>
                <div class="custom-control custom-checkbox form-check-inline mt-2">
                  <input type="checkbox" name="bed_off_on_pause" class="custom-control-input" id="id_bed_off_on_pause">
                  <label class="custom-control-label" for="id_bed_off_on_pause">
                    Turn off bed heater
                  </label>
                </div>
                <div class="form-inline my-1">
                  <div class="custom-control custom-checkbox form-check-inline">
                    <input type="checkbox" class="custom-control-input" id="retract-checkbox">
                    <label class="custom-control-label" for="retract-checkbox">Retract filament by</label>
                  </div>
                  <div class="input-group input-group-sm minimal-width">
                    <input type="number" name="retract_on_pause" value="6.5" step="0.5" aria-label="Retraction ammount in millimeters" min="0" class="form-control field_required" required="" id="id_retract_on_pause">
                    <div class="input-group-append">
                      <span class="input-group-text">mm</span>
                    </div>
                  </div>
                </div>
                <div class="form-inline my-1">
                  <div class="custom-control custom-checkbox form-check-inline">
                    <input type="checkbox" class="custom-control-input" id="lift-z-checkbox">
                    <label class="custom-control-label" for="lift-z-checkbox">Lift extruder along Z axis by</label>
                  </div>
                  <div class="input-group input-group-sm minimal-width">
                    <input type="number" name="lift_z_on_pause" value="2.5" step="0.5" aria-label="Lift Z Axis ammount in millimeters" min="0" class="form-control field_required" required="" id="id_lift_z_on_pause">
                    <div class="input-group-append">
                      <span class="input-group-text">mm</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="form-group sensitivity my-4">
                <div class="form-label text-muted">How sensitive do you want the Detective to be on this printer?</div>
                <div class="px-3 my-2">
                  <input id="sensitivity" name="detective_sensitivity" data-slider-id='sensitivity-slider' type="text"
                    data-slider-min="0.8" data-slider-max="1.2" data-slider-step="0.05" data-slider-value="1" />
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
import JQuery from 'jquery'
import Slider from 'bootstrap-slider'

export default {
  name: 'PrinterPreferences',

  mounted() {
    const $ = JQuery
    console.log(Slider)

    $('#sensitivity').slider({
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

    function updateSensitivityHint() {
      $('.sensitivity div[class^=hint]').hide()
      var value = parseFloat($('#sensitivity').val())
      if (value < 0.95) {
        $('.sensitivity .hint-low').show()
      } else if (value > 1.05) {
        $('.sensitivity .hint-high').show()
      } else {
        $('.sensitivity .hint-medium').show()
      }
    }

    $('#sensitivity').on('change', updateSensitivityHint)
    updateSensitivityHint()
  },
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.form-label
  font-size: 20px

.custom-control-label
  font-size: 16px

.input-group.minimal-width input
  width: 4rem

// .sensitivity .tooltip
//   position: relative
//   bottom: 10px !important
</style>