<template>
  <widget-template>
    <template #title>
      <div v-if="activeMenu" class="nav-btn" @click="activeMenu = null">
        <i class="fas fa-arrow-left"></i>&nbsp;&nbsp;{{$t("Back")}}
      </div>
      <span v-else>{{ $t("Printer Controls") }}</span>
    </template>
    <template #content>
      <div class="wrapper">
        <div v-show="!activeMenu" class="home-menu">
          <button
            class="menu-button"
            :disabled="printer.isActive()"
            @click="activeMenu = 'move-head'"
          >
            <svg class="icon move-xy"><use href="#svg-move-xy" /></svg>
            <div class="title">{{ $t("Move Head") }}</div>
          </button>
          <button
            class="menu-button"
            :disabled="printer.isActive()"
            @click="activeMenu = 'extrude'"
          >
            <svg class="icon extruder"><use href="#extruder" /></svg>
            <div class="title">{{ $t("Extrude") }}</div>
          </button>
          <button
            v-if="printer.isAgentMoonraker()"
            class="menu-button"
            @click="activeMenu = 'baby-step-z'"
          >
            <svg class="icon move-z"><use href="#svg-move-z" /></svg>
            <div class="title">{{ $t("Baby Step Z") }}</div>
          </button>
          <button v-if="!hideTunePrinter" class="menu-button" @click="activeMenu = 'tune-printer'">
            <font-awesome-icon :icon="['fas', 'gear']" />
            <div class="title">{{ $t("Tune Printer") }}</div>
          </button>
          <button
            v-if="powerDevices.length"
            class="menu-button"
            @click="activeMenu = 'power-control'"
          >
            <font-awesome-icon :icon="['fas', 'power-off']" />
            <div class="title">{{ $t("Power") }}</div>
          </button>
        </div>

        <!-- Move Head -->
        <div v-show="activeMenu === 'move-head'" class="control-panel move-head">
          <div class="main">
            <div class="toggles">
              <div
                v-for="option in xyzJogDistance.options"
                :key="'xyz-' + option"
                class="pill"
                :class="{ active: option === xyzJogDistance.value }"
                @click="xyzJogDistance.value = option"
              >
                {{ option }}
              </div>
            </div>
            <div class="xy-move">
              <div class="left" @click="xyzControl(axis.x, directions.down)">
                <i class="fas fa-arrow-left"></i>
              </div>
              <div class="right" @click="xyzControl(axis.x, directions.up)">
                <i class="fas fa-arrow-right"></i>
              </div>
              <div class="up" @click="xyzControl(axis.y, directions.up)">
                <i class="fas fa-arrow-up"></i>
              </div>
              <div class="down" @click="xyzControl(axis.y, directions.down)">
                <i class="fas fa-arrow-down"></i>
              </div>
              <div class="home" @click="xyzControl(axis.xy, directions.home)">
                <i class="fas fa-home"></i>
              </div>
            </div>
            <div class="z-move">
              <div class="up" @click="xyzControl(axis.z, directions.up)">
                <i class="fas fa-arrow-up"></i>
              </div>
              <div class="down" @click="xyzControl(axis.z, directions.down)">
                <i class="fas fa-arrow-down"></i>
              </div>
              <div class="home" @click="xyzControl(axis.z, directions.home)">
                <i class="fas fa-home"></i>
              </div>
            </div>
          </div>
          <div class="additional">
            <div class="control-btn" @click="homeAll"><i class="fas fa-home"></i>{{ $t(" Home All") }}</div>
            <div class="control-btn" @click="disableSteppers">
              <i class="fas fa-power-off"></i> {{$t("Disable Steppers")}}
            </div>
          </div>
        </div>

        <!-- Extrude -->
        <div v-show="activeMenu === 'extrude'" class="control-panel extrude">
          <div class="main">
            <template v-if="showExtrudeControl">
              <div class="toggles">
                <div
                  v-for="option in extrudeJogDistance.options"
                  :key="'xyz-' + option"
                  class="pill"
                  :class="{ active: option === extrudeJogDistance.value }"
                  @click="extrudeJogDistance.value = option"
                >
                  {{ option }}
                </div>
              </div>
              <div class="main-buttons">
                <div class="control-btn" @click="handleFilament(filamentDirections.retract)">
                  <i class="fas fa-minus"></i> {{$t("Retract")}}
                </div>
                <div class="control-btn" @click="handleFilament(filamentDirections.extrude)">
                  <i class="fas fa-plus"></i> {{$t("Extrude")}}
                </div>
              </div>
            </template>
            <template v-else>
              <div class="text-center mt-4">
                <b-spinner></b-spinner>
                <p class="mt-2">{{ $t("Loading tools...") }}</p>
              </div>
            </template>
          </div>
          <div v-if="showToolsSelector" class="additional">
            <b-form-select v-model="activeTool" class="form-control tool-select">
              <b-form-select-option v-for="(item, key) in tools" :key="key" :value="key">
                {{ temperatureDisplayName(key) }}
              </b-form-select-option>
            </b-form-select>
          </div>
        </div>

        <!-- Baby Step Z -->
        <div v-show="activeMenu === 'baby-step-z'" class="control-panel baby-step-z">
          <div class="main">
            <div class="toggles">
              <div
                v-for="option in zOffsetJogDistance.options"
                :key="'xyz-' + option"
                class="pill"
                :class="{ active: option === zOffsetJogDistance.value }"
                @click="zOffsetJogDistance.value = option"
              >
                {{ option }}
              </div>
            </div>
            <div class="z-move">
              <div class="up" @click="controlZOffset(directions.up)">
                <i class="fas fa-arrow-up"></i>
              </div>
              <div class="down" @click="controlZOffset(directions.down)">
                <i class="fas fa-arrow-down"></i>
              </div>
            </div>
          </div>
          <div class="additional">
            <div class="current-offset">
              <div class="label">{{ $t("Current Offset") }}</div>
              <div class="value">
                <span v-if="currentZOffset || typeof currentZOffset === 'number'">
                  {{ currentZOffset }}
                </span>
                <span v-else>
                  <b-spinner small></b-spinner>
                </span>
              </div>
            </div>
          </div>
        </div>
        <!-- Tune Printer -->
        <div v-show="activeMenu === 'tune-printer'" class="control-panel tune-printer">
          <template v-if="!printer.isAgentMoonraker() || currentFeedRate !== null">
            <div class="controls-title">
              <span>{{ $t("Feed Rate / Speed") }}</span>
              <help-widget id="print-speed-widget-help" class="help-message"></help-widget>
            </div>
            <div class="controls">
              <div class="custom">
                <b-input-group prepend="%">
                  <template #append>
                    <b-button
                      variant="background"
                      :disabled="
                        customFeedRateFactor === null || parseInt(customFeedRateFactor) < 1
                      "
                      @click="setPrintSpeed(customFeedRateFactor)"
                      >{{ $t("Apply") }}</b-button
                    >
                  </template>
                  <b-form-input
                    v-model="customFeedRateFactor"
                    placeholder="100"
                    type="number"
                    @focus="$event.target.select()"
                  ></b-form-input>
                </b-input-group>
              </div>
            </div>
          </template>

          <template v-if="!printer.isAgentMoonraker() || currentFlowRate !== null">
            <div class="controls-title">
              <span>{{ $t("Flow Rate") }}</span>
              <help-widget id="flow-rate-widget-help" class="help-message"></help-widget>
            </div>
            <div class="controls">
              <div class="custom">
                <b-input-group prepend="%">
                  <template #append>
                    <b-button
                      variant="background"
                      :disabled="
                        customFlowRateFactor === null || parseInt(customFlowRateFactor) < 1
                      "
                      @click="setFlowRate(customFlowRateFactor)"
                      >{{ $t("Apply") }}</b-button
                    >
                  </template>
                  <b-form-input
                    v-model="customFlowRateFactor"
                    placeholder="100"
                    type="number"
                    @focus="$event.target.select()"
                  ></b-form-input>
                </b-input-group>
              </div>
            </div>
          </template>

          <template v-if="!printer.isAgentMoonraker() || currentFanSpeed !== null">
            <div class="controls-title">
              <span>{{ $t("Fan Speed") }}</span>
              <help-widget id="fan-speed-widget-help" class="help-message"></help-widget>
            </div>
            <div class="controls">
              <b-button
                class="off"
                variant="background"
                small
                @click="
                  {
                    customFanSpeed = 0
                    setFanSpeed(0)
                  }
                "
                >{{ $t("0% (Off)") }}</b-button
              >
              <div class="custom">
                <b-input-group prepend="%">
                  <template #append>
                    <b-button
                      variant="background"
                      :disabled="
                        customFanSpeed === null ||
                        parseInt(customFanSpeed) > 100 ||
                        parseInt(customFanSpeed) < 0
                      "
                      @click="setFanSpeed(customFanSpeed)"
                      >{{ $t("Apply") }}</b-button
                    >
                  </template>
                  <b-form-input
                    v-model="customFanSpeed"
                    placeholder="0-100"
                    type="number"
                    @focus="$event.target.select()"
                  ></b-form-input>
                </b-input-group>
              </div>
              <b-button
                class="btn"
                variant="background"
                small
                @click="
                  {
                    customFanSpeed = 100
                    setFanSpeed(100)
                  }
                "
                >100%</b-button
              >
            </div>
          </template>

          <muted-alert v-if="!printer.isAgentMoonraker()" class="info-block">
            {{$t("These settings can only be set. They can't be read back from the firmware due to a limitation of the communication protocol.")}}
          </muted-alert>
        </div>

        <!-- Power Control -->
        <div v-show="activeMenu === 'power-control'" class="control-panel power-control">
          <div v-for="(item, index) in powerDevices" :key="index" class="power-item">
            <div class="title">
              <div class="name">{{ item.device }}</div>
              <div
                class="status text-danger"
                :class="{ 'text-success': item.status.toUpperCase() === 'ON' }"
              >
                • {{ item.status.toUpperCase() }}
              </div>
            </div>
            <b-button variant="outline-primary" @click="togglePower(item)">{{ $t(" Toggle Power ") }}</b-button>
          </div>

          <div v-if="powerDevices.length > 1" class="bulk-actions">
            <b-button variant="success" @click="batchPowerControl('on')">{{ $t(" Power On All ") }}</b-button>
            <b-button variant="danger" @click="batchPowerControl('off')">{{ $t(" Power Off All ") }}</b-button>
          </div>

          <muted-alert class="info-block">
            {{$t("Rapid toggling power may result in error. Please allow a cooldown period.")}}
          </muted-alert>
        </div>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import { isLocalStorageSupported } from '@static/js/utils'
import get from 'lodash/get'
import { temperatureDisplayName } from '@src/lib/utils'
import HelpWidget from '@src/components/HelpWidget.vue'
import MutedAlert from '@src/components/MutedAlert.vue'

const AXIS = {
  x: 'x',
  y: 'y',
  z: 'z',
  xy: ['x', 'y'],
  xyz: ['x', 'y', 'z'],
}

const DIRECTIONS = {
  up: 1,
  down: -1,
  home: 0,
}

const FILAMENT_DIRECTIONS = {
  retract: -1,
  extrude: 1,
}

export default {
  name: 'PrinterControlWidget',

  components: {
    WidgetTemplate,
    HelpWidget,
    MutedAlert,
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
      activeMenu: null, // 'move-head' | 'extrude' | 'baby-step-z'

      axis: AXIS,
      directions: DIRECTIONS,
      filamentDirections: FILAMENT_DIRECTIONS,

      xyzJogDistance: {
        value: 10,
        options: [1, 10, 50, 100],
      },
      extrudeJogDistance: {
        value: 10,
        options: [1, 10, 50],
      },
      zOffsetJogDistance: {
        value: 0.01,
        options: [0.005, 0.01, 0.05, 0.1],
      },
      activeTool: null,

      currentZOffset: null,

      customFeedRateFactor: null,
      customFlowRateFactor: null,
      customFanSpeed: null,

      powerDevices: [],
    }
  },

  computed: {
    tools() {
      const extruders = {}
      for (const [key, value] of Object.entries(get(this.printer, 'status.temperatures', {}))) {
        if (
          Boolean(value.actual) &&
          !isNaN(value.actual) &&
          (key.toLowerCase().includes('tool') || key.toLowerCase().includes('extruder'))
        ) {
          // Take out NaN, 0, null. Apparently printers like Prusa throws random temperatures here.
          extruders[key] = value
        }
      }
      return extruders
    },
    showExtrudeControl() {
      return Object.keys(this.tools).length > 0
    },
    showToolsSelector() {
      return Object.keys(this.tools).length > 1
    },
    currentFeedRate() {
      const val = this.printer.status?.currentFeedRate
      return val !== undefined ? val : null
    },
    currentFlowRate() {
      const val = this.printer.status?.currentFlowRate
      return val !== undefined ? val : null
    },
    currentFanSpeed() {
      const val = this.printer.status?.currentFanSpeed
      return val !== undefined ? val : null
    },
    hideTunePrinter() {
      return (
        this.printer.isAgentMoonraker() &&
        this.currentFlowRate === null &&
        this.currentFanSpeed === null &&
        this.currentFeedRate === null
      )
    },
  },

  watch: {
    tools: {
      handler: function (newValue, prevValue) {
        if (newValue) {
          this.activeTool = Object.keys(newValue)[0]
        }
      },
      immediate: true,
    },
    printer: {
      handler: function (newValue, oldValue) {
        if (newValue.isActive() && ['move-head', 'extrude'].includes(this.activeMenu)) {
          this.activeMenu = null
        }
      },
      deep: true,
    },
    xyzJogDistance: {
      handler: function (newValue, oldValue) {
        if (isLocalStorageSupported()) {
          localStorage.setItem(`xyz-mm-per-step-${this.printer.id}`, newValue.value)
        }
      },
      deep: true,
    },
    extrudeJogDistance: {
      handler: function (newValue, oldValue) {
        if (isLocalStorageSupported()) {
          localStorage.setItem(`extrude-mm-per-step-${this.printer.id}`, newValue.value)
        }
      },
      deep: true,
    },
    zOffsetJogDistance: {
      handler: function (newValue, oldValue) {
        if (isLocalStorageSupported()) {
          localStorage.setItem(`z-offset-mm-per-step-${this.printer.id}`, newValue.value)
        }
      },
      deep: true,
    },
    activeMenu(newValue, oldValue) {
      if (newValue === 'baby-step-z') {
        this.getCurrentZOffset()
      } else if (newValue === 'tune-printer') {
        this.customFeedRateFactor =
          this.currentFeedRate !== null ? Math.round(this.currentFeedRate * 100) : null
        this.customFlowRateFactor =
          this.currentFlowRate !== null ? Math.round(this.currentFlowRate * 100) : null
        this.customFanSpeed =
          this.currentFanSpeed !== null ? Math.round(this.currentFanSpeed * 100) : null
      }
    },
  },

  created() {
    this.getPowerDevices()

    // Get jogDistance from localStorage or set default value
    if (isLocalStorageSupported()) {
      this.xyzJogDistance.value =
        +localStorage.getItem(`xyz-mm-per-step-${this.printer.id}`) || this.xyzJogDistance.value

      this.extrudeJogDistance.value =
        +localStorage.getItem(`extrude-mm-per-step-${this.printer.id}`) ||
        this.extrudeJogDistance.value

      this.zOffsetJogDistance.value =
        +localStorage.getItem(`z-offset-mm-per-step-${this.printer.id}`) ||
        this.zOffsetJogDistance.value
    }

    // Listen for ESC key to close active menu
    const onEscape = (e) => {
      if (e.keyCode === 27) {
        this.activeMenu = null
      }
    }
    document.addEventListener('keydown', onEscape)
    this.$once('hook:destroyed', () => {
      document.removeEventListener('keydown', onEscape)
    })
  },

  methods: {
    // XYZ Control
    xyzControl(axis, direction) {
      let args = []
      let func = 'jog'
      if (direction === this.directions.home) {
        args.push(axis)
        func = 'home'
      } else {
        args.push({ [axis]: direction * this.xyzJogDistance.value })
      }
      const payload = { func: func, target: '_printer', args: args }
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        }
      })
    },
    getCurrentZOffset() {
      const moonrakerPayload = { func: 'printer/objects/query?gcode_move', target: 'moonraker_api' }
      this.printerComm.passThruToPrinter(moonrakerPayload, (err, ret) => {
        if (err) {
          this.currentZOffset = 'no reading'
        } else {
          const offset = ret.status.gcode_move.homing_origin[2]
          const cleanOffset = parseFloat(offset.toFixed(3))
          this.currentZOffset = cleanOffset
        }
      })
    },
    homeAll() {
      this.xyzControl(this.axis.xyz, this.directions.home)
    },
    disableSteppers() {
      const octoPayload = { func: 'commands', target: '_printer', args: ['M18'] }
      const moonrakerPayload = {
        func: 'printer/gcode/script',
        target: 'moonraker_api',
        kwargs: { script: 'M18' },
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
    },

    // Extrude / Retract
    temperatureDisplayName,
    handleFilament(direction) {
      const currentToolTemp = this.tools[this.activeTool].actual
      if (currentToolTemp < 179) {
        this.$swal.Confirm.fire({
          title: `${this.$i18next.t('Unable to extrude / retract')}`,
          html: `<p class="text-center">${this.$i18next.t("The hotend is below the minimum temperature")}</p>`,
          confirmButtonText: `${this.$i18next.t('Heat to 180°C')}`,
          cancelButtonText: `${this.$i18next.t('Cancel')}`,
        }).then((result) => {
          if (result.isConfirmed) {
            this.printerComm.passThruToPrinter(
              { func: 'set_temperature', target: '_printer', args: [this.activeTool, 180] },
              (err, ret) => {
                if (err) {
                  this.$swal.Toast.fire({
                    icon: 'error',
                    title: err,
                  })
                }
              }
            )
          }
        })

        return
      }

      const toolNum = Object.entries(this.tools).findIndex((t) => t[0] === this.activeTool)
      const changeAmount = direction * this.extrudeJogDistance.value
      const commandScript = `M83\nT${toolNum}\nG1 E${changeAmount} F300`

      const octoPayload = { func: 'commands', target: '_printer', args: [commandScript] }
      const moonrakerPayload = {
        func: 'printer/gcode/script',
        target: 'moonraker_api',
        kwargs: { script: commandScript },
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
    },

    // Baby Step Z
    controlZOffset(direction) {
      const changeAmount = this.zOffsetJogDistance.value * direction
      const octoVal = Math.round(changeAmount * 10000) / 10000
      const moonrakerVal = octoVal > 0 ? `+${octoVal}` : `${octoVal}`
      const octoPayload = {
        func: 'commands',
        target: '_printer',
        args: [`M290 Z ${octoVal}`],
        force: true,
      }
      const moonrakerPayload = {
        func: 'printer/gcode/script',
        target: 'moonraker_api',
        kwargs: { script: `SET_GCODE_OFFSET Z_ADJUST=${moonrakerVal}` },
      }
      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
      this.currentZOffset = null
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        } else {
          this.getCurrentZOffset()
        }
      })
    },

    // Print Speed / Flow Rate / Fan Speed
    setPrintSpeed(value) {
      if (value === null || value < 1) return
      this.sendCommandToPrinter(`M220 S${Math.round(value)}`)
    },
    setFlowRate(value) {
      if (value === null || value < 1) return
      this.sendCommandToPrinter(`M221 S${Math.round(value)}`)
    },
    setFanSpeed(value) {
      if (value === null || value < 0 || value > 100) return
      let command = value === 0 ? 'M107' : `M106 S${Math.round((value / 100) * 255)}`
      this.sendCommandToPrinter(command)
    },
    sendCommandToPrinter(command, { onError, onSuccess } = {}) {
      const payload = this.printer.isAgentMoonraker()
        ? {
            func: 'printer/gcode/script',
            target: 'moonraker_api',
            kwargs: { script: command },
          }
        : {
            func: 'commands',
            target: '_printer',
            args: [command],
          }

      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          if (onError) {
            onError(err, ret)
          } else {
            this.$swal.Toast.fire({
              icon: 'error',
              title: err,
            })
          }
        } else {
          if (onSuccess) {
            onSuccess(err, ret)
          } else {
            this.$swal.Toast.fire({
              icon: 'success',
              title: `${this.$i18next.t('Command successfully sent!')}`,
            })
          }
        }
      })
    },

    // Power Control
    getPowerDevices() {
      if (!this.printer.isAgentMoonraker()) return
      const moonrakerPayload = {
        func: 'machine/device_power/devices',
        target: 'moonraker_api',
        args: [],
      }
      this.printerComm.passThruToPrinter(moonrakerPayload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        } else {
          this.powerDevices = ret?.devices || []
        }
      })
    },
    togglePower(device) {
      // same as above but adapted to this file passThru function and syntax
      const actionString = device.status.toUpperCase() === 'ON' ? 'off' : 'on'
      const deviceStr = `device=${device.device}&action=${actionString}`
      const moonrakerPayload = {
        func: `machine/device_power/device?${deviceStr}`,
        target: 'moonraker_api',
        kwargs: { verb: 'post' },
      }
      this.printerComm.passThruToPrinter(moonrakerPayload, (err, ret) => {
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
      if (!this.powerDevices.length) return
      const str = `${this.powerDevices.map((obj) => obj.device).join('&')}`
      const moonrakerPayload = {
        func: `machine/device_power/${action}?${str}`,
        target: 'moonraker_api',
        kwargs: { verb: 'post' },
      }
      this.printerComm.passThruToPrinter(moonrakerPayload, (err, ret) => {
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
.nav-btn
  display: inline-block
  color: var(--color-text-primary)
  cursor: pointer

.wrapper
  padding-bottom: 1.5rem
  min-height: 260px
  display: flex
  justify-content: center
  align-items: center

.home-menu
  display: flex
  flex-direction: row
  justify-content: center
  gap: 1rem
  width: 100%
  flex-wrap: wrap
  @media (max-width: 510px)
    gap: .5rem

.menu-button
  width: calc((100% - 3rem) / 3)
  flex-shrink: 0
  padding: 1.5rem 1rem
  background-color: var(--color-background)
  color: var(--color-text-primary)
  border: none
  border-radius: var(--border-radius-md)
  display: flex
  flex-direction: column
  align-items: center
  justify-content: center
  gap: .5rem
  cursor: pointer
  @media (max-width: 510px)
    width: calc((100% - 2rem) / 3)
    padding: 1rem 0.5rem
  &:hover
    opacity: .8
  &:disabled
    opacity: .5
    cursor: not-allowed
  i, svg
    font-size: 1.75rem
    @media (max-width: 510px)
      font-size: 1.2rem
.icon
  --icon-size: 42px
  width: var(--icon-size)
  height: var(--icon-size)
  color: var(--color-text-primary)
  &.move-xy
    --icon-size: 38px
  &.extruder
    --icon-size: 36px
  @media (max-width: 510px)
    --icon-size: 24px !important
.title
  font-size: 0.875rem
  line-height: 1.2


.control-panel
  width: 100%
  .main
    display: flex
    align-items: center
    justify-content: center
    gap: 2rem
    margin-bottom: 2rem
    @media (max-width: 510px)
      gap: 1rem
  .toggles
    display: flex
    flex-direction: column
    gap: .5rem
  .pill
    padding: .25rem
    width: 3.5rem
    background-color: var(--color-secondary)
    color: var(--color-on-secondary)
    border-radius: 999px
    font-size: 0.875rem
    text-align: center
    cursor: pointer
    &.active
      background-color: var(--color-primary)
      color: var(--color-on-primary)
  .xy-move, .z-move
    width: 146px
    height: 146px
    border-radius: var(--border-radius-md)
    background-color: var(--color-background)
    color: var(--color-text-primary)
    position: relative
    .left, .right, .up, .down, .home
      position: absolute
      width: 42px
      height: 42px
      font-size: 1.25rem
      text-align: center
      line-height: 42px
      margin: auto
      left: 0
      right: 0
      top: 0
      bottom: 0
      cursor: pointer
      &:hover
        opacity: .8
    .left
      right: unset
    .right
      left: unset
    .up
      bottom: unset
    .down
      top: unset

  .z-move
    width: 60px
  .additional
    display: flex
    justify-content: center
    gap: 1rem
  .control-btn
    display: flex
    align-items: center
    gap: .5rem
    cursor: pointer
    background-color: var(--color-background)
    border-radius: var(--border-radius-sm)
    color: var(--color-text-primary)
    padding: .5rem 1rem
    font-size: 0.875rem
    &:hover
      opacity: .8

.current-offset
  display: flex
  gap: 1rem
  border: 1px solid var(--color-divider-muted)
  border-radius: var(--border-radius-sm)
  color: var(--color-text-primary)
  padding: .5rem 1rem
  font-size: 0.875rem
  .value
    font-weight: bold

.main-buttons
  display: flex
  flex-direction: column
  gap: 1rem
  .control-btn
    font-size: 1rem
    border-radius: var(--border-radius-md)
    padding: .625rem 1.5rem

.tool-select
  width: 80%

.tune-printer
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem

  .controls-title
    font-size: 1rem
    width: 100%
    display: flex
    gap: .375rem
  .controls
    width: 100%
    display: flex
    gap: .75rem
    margin-bottom: 1rem

    .off
      flex-shrink: 0
      width: 100px

    .custom
      border-radius: 100px
      overflow: hidden
      flex: 1

    ::v-deep .input-group-text
      background-color: var(--color-divider)
      color: var(--color-text-primary)

    @media (max-width: 510px)
      flex-direction: column
      .off
        width: 100%

  .info-block
    width: 100%

.power-control
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
</style>
