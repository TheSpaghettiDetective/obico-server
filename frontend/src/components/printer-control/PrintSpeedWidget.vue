<template>
  <widget-template>
    <template #title>Print Speed Factor (Feed Rate)</template>
    <template #content>
      <slot name="content">
        <div class="wrapper">
          <help-widget id="print-speed-widget-help" class="help-message"></help-widget>
          <div class="controls">
            <div class="custom">
              <b-input-group prepend="%">
                <template #append>
                  <b-button
                    variant="background"
                    :disabled="
                      customSpeed === null ||
                      parseInt(customSpeed) > maxValue ||
                      parseInt(customSpeed) < 1
                    "
                    @click="setSpeed(customSpeed)"
                    >Apply</b-button
                  >
                </template>
                <b-form-input
                  v-model="customSpeed"
                  placeholder="1-200"
                  type="number"
                ></b-form-input>
              </b-input-group>
            </div>
          </div>
        </div>
      </slot>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import HelpWidget from '@src/components/HelpWidget.vue'

export default {
  name: 'PrintSpeedWidget',

  components: {
    WidgetTemplate,
    HelpWidget,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
    printerComm: {
      type: Object,
      required: true,
    },
  },

  data: function () {
    return {
      customSpeed: null,
      maxValue: 200,
    }
  },

  methods: {
    setSpeed(value) {
      if (value === null || value < 1 || value > this.maxValue) return

      const payload = {
        func: 'commands',
        target: '_printer',
        args: [`M220 S${Math.round(value)}`],
      }

      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err || ret?.error) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: ret.error,
          })
        } else {
          this.customSpeed = null
          this.$swal.Toast.fire({
            icon: 'success',
            title: 'Command successfully sent!',
          })
        }
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem

.help-message
  position: absolute
  top: 8px
  right: 12px

.custom
  border-radius: 100px
  overflow: hidden

::v-deep .input-group-text
  background-color: var(--color-divider)
  color: var(--color-text-primary)
</style>
