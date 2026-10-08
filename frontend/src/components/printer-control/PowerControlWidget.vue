<template>
  <widget-template v-if="availablePowerDevices.length">
    <template #title>{{ $t("Power") }}</template>
    <template #content>
      <div class="power-control">
        <div v-for="item in availablePowerDevices" :key="item.device" class="power-item">
          <div class="title">
            <div class="name">{{ item.device }}</div>
            <div
              class="status text-danger"
              :class="{ 'text-success': item.status.toUpperCase() === 'ON' }"
            >
              • {{ item.status.toUpperCase() }}
            </div>
          </div>
          <b-button variant="outline-primary" @click="togglePower(item)">
            {{ $t(" Toggle Power ") }}
          </b-button>
        </div>

        <div v-if="availablePowerDevices.length > 1" class="bulk-actions">
          <b-button variant="success" @click="batchPowerControl('on')">
            {{ $t(" Power On All ") }}
          </b-button>
          <b-button variant="danger" @click="batchPowerControl('off')">
            {{ $t(" Power Off All ") }}
          </b-button>
        </div>

        <muted-alert class="info-block">
          {{$t("Rapid toggling power may result in error. Please allow a cooldown period.")}}
        </muted-alert>
      </div>
    </template>
  </widget-template>
</template>

<script>
import MutedAlert from '@src/components/MutedAlert.vue'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'

export default {
  name: 'PowerControlWidget',

  components: {
    MutedAlert,
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

  data() {
    return {
      powerDevices: [],
    }
  },

  computed: {
    availablePowerDevices() {
      if (!this.printer.isOffline() && !this.printer.isDisconnected()) {
        return this.powerDevices
      }

      return this.powerDevices.filter(device => device.type !== 'klipper_device')
    },
  },

  created() {
    this.getPowerDevices()
  },

  methods: {
    getPowerDevices() {
      const payload = {
        func: 'machine/device_power/devices',
        target: 'moonraker_api',
        args: [],
      }
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        this.powerDevices = err ? [] : ret?.devices || []
      })
    },
    togglePower(device) {
      const action = device.status.toUpperCase() === 'ON' ? 'off' : 'on'
      const payload = {
        func: `machine/device_power/device?device=${device.device}&action=${action}`,
        target: 'moonraker_api',
        kwargs: { verb: 'post' },
      }
      this.printerComm.passThruToPrinter(payload, (err) => {
        this.getPowerDevices()
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        }
      })
    },
    batchPowerControl(action) {
      if (!this.availablePowerDevices.length) return

      const devices = this.availablePowerDevices.map(device => device.device).join('&')
      const payload = {
        func: `machine/device_power/${action}?${devices}`,
        target: 'moonraker_api',
        kwargs: { verb: 'post' },
      }
      this.printerComm.passThruToPrinter(payload, (err) => {
        this.getPowerDevices()
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        }
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.power-control
  padding-bottom: .5rem
  .power-item
    margin: 1rem 0
    display: flex
    flex-direction: column
    gap: .5rem
  .title
    display: flex
    justify-content: space-between
    font-size: 1rem
    font-weight: bold
  .bulk-actions
    display: flex
    gap: 1rem
    margin: 2rem 0
    button
      flex: 1
  .info-block
    width: 100%
</style>
