<template>
  <widget-template>
    <template #title>Fan Speed</template>
    <template #content>
      <slot name="content">
        <div class="wrapper">
          <help-widget id="fan-speed-widget-help" class="help-message"></help-widget>
          <div class="controls">
            <b-button class="off" variant="background" small @click="turnOff">0% (off)</b-button>
            <div class="custom">
              <b-input-group prepend="%">
                <template #append>
                  <b-button
                    variant="background"
                    :disabled="
                      customSpeed === null ||
                      parseInt(customSpeed) > 100 ||
                      parseInt(customSpeed) < 0
                    "
                    @click="setSpeed(customSpeed)"
                    >Apply</b-button
                  >
                </template>
                <b-form-input
                  v-model="customSpeed"
                  placeholder="0-100"
                  type="number"
                ></b-form-input>
              </b-input-group>
            </div>
            <b-button class="btn" variant="background" small @click="turnFull">100%</b-button>
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
  name: 'FanSpeedWidget',

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
    }
  },

  computed: {},

  methods: {
    turnOff() {
      this.setSpeed(0)
    },
    turnFull() {
      this.setSpeed(100)
    },

    setSpeed(value) {
      if (value === null || value < 0 || value > 100) return

      const payload = {
        func: 'commands',
        target: '_printer',
        args: [`M107`],
      }

      if (value > 0) {
        const val = Math.round((value / 100) * 255) // 255 equals to 100%
        payload.args = [`M106 S${val}`]
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

.controls
  width: 100%
  display: flex
  gap: .75rem

  .off
    flex-shrink: 0
    width: 100px

  .custom
    border-radius: 100px
    overflow: hidden

  ::v-deep .input-group-text
    background-color: var(--color-divider)
    color: var(--color-text-primary)

  @media (max-width: 510px)
    flex-direction: column
    .off
      width: 100%
</style>
