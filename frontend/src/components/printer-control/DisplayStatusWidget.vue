<template>
  <widget-template>
    <template #title>{{ $t("LCD Display Message") }}</template>
    <template #content>
      <div class="wrapper">
        <div class="message-content">
          <p class="text">{{ printer.status.display_status.message }}</p>
        </div>
        <b-button variant="outline-primary" class="dismiss-btn" @click="onDisplayClear">
          {{ $t("Dismiss") }}
        </b-button>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'

export default {
  name: 'DisplayStatusWidget',

  components: {
    WidgetTemplate,
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

  methods: {
    onDisplayClear() {
      const octoPayload = {
        func: 'commands',
        target: '_printer',
        args: ["M117"],
        force: true,
      }
      const moonrakerPayload = {
        func: 'printer/gcode/script',
        target: 'moonraker_api',
        kwargs: {"script": "SET_DISPLAY_TEXT"},
      }
      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload

      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        }
      })
    }
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: row
  align-items: center
  justify-content: space-between
  gap: 1rem
  padding-bottom: 1rem

.message-content
  display: flex
  align-items: center
  justify-content: flex-start
  flex: 1
  min-width: 0

.text
  margin: 0
  font-size: 1.5rem
  font-weight: bold
  color: var(--color-warning)
  word-break: break-word
  overflow-wrap: break-word
  text-align: left
  line-height: 1.4

.dismiss-btn
  flex-shrink: 0
</style>
