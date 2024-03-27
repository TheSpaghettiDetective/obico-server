<template>
  <widget-template>
    <template #title>{{ $t("Temperature Controls") }}</template>
    <template #content>
      <slot name="content">
        <div class="wrapper">
          <template v-if="show">
            <temperature-item
              v-for="(item, key) in temperatures"
              :key="key"
              :temp-key="key"
              :temp-item="item"
              :is-plugin-version-sufficient="isPluginVersionSufficient"
              @TempEditClicked="onEditClicked(key, item)"
            />
            <b-button
              v-if="isPluginVersionSufficient"
              variant="outline-primary"
              class="custom-button"
              @click="onTemperaturePresetsClicked"
            >
              {{$t("Temperature Presets")}}
            </b-button>
          </template>
          <template v-else>
            <div class="text-center mt-4">
              <b-spinner></b-spinner>
              <p class="mt-2">{{ $t("Loading temperature...") }}</p>
            </div>
          </template>
        </div>
      </slot>
    </template>
  </widget-template>
</template>

<script>
import TempTargetEditor from '@src/components/printers/TempTargetEditor.vue'
import TempPresets from '@src/components/printers/TempPresets.vue'
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import get from 'lodash/get'
import { temperatureDisplayName } from '@src/lib/utils'
import TemperatureItem from '@src/components/printers/TemperatureItem.vue'

export default {
  name: 'TemperatureWidget',

  components: {
    WidgetTemplate,
    TemperatureItem,
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

  computed: {
    temperatures() {
      const temperatures = {}
      for (const [key, value] of Object.entries(get(this.printer, 'status.temperatures', {}))) {
        if (Boolean(value.actual) && !isNaN(value.actual)) {
          // Take out NaN, 0, null. Apparently printers like Prusa throws random temperatures here.
          temperatures[key] = value
        }
      }
      return temperatures
    },
    isPluginVersionSufficient() {
      // If temp_profiles is missing, it's a plugin version too old to change temps
      return get(this.printer, 'settings.temp_profiles') != undefined
    },
    show() {
      return Object.keys(this.temperatures).length > 0
    },
  },

  methods: {
    temperatureDisplayName,
    onEditClicked(key, item) {
      if (!this.isPluginVersionSufficient || item.target === null) {
        return
      }

      let tempProfiles = get(this.printer, 'settings.temp_profiles', [])
      let presets
      let maxTemp = 350

      if (key.search(/bed|chamber/) > -1) {
        maxTemp = 140
      }
      if (key.search(/tool/) > -1) {
        // OctoPrint uses 'extruder' for toolx heaters
        presets = tempProfiles.map((v) => {
          return { name: v.name, target: v['extruder'] }
        })
      } else {
        presets = tempProfiles.map((v) => {
          return { name: v.name, target: v[key] }
        })
      }

      this.$swal
        .openModalWithComponent(
          TempTargetEditor,
          {
            presets: presets,
            maxTemp: maxTemp,
            curTarget: item.target,
          },
          {
            title: 'Set ' + temperatureDisplayName(key) + ' Temperature',
            confirmButtonText: 'Confirm',
            showCancelButton: true,
            preConfirm: () => {
              return {
                target: parseInt(document.getElementById('target-temp').value),
              }
            },
          }
        )
        .then((result) => {
          if (result.value) {
            let targetTemp = result.value.target
            this.handleSetTemp(key, targetTemp)
          }
        })
    },
    onTemperaturePresetsClicked() {
      let tempProfiles = get(this.printer, 'settings.temp_profiles', [])

      this.$swal
        .openModalWithComponent(
          TempPresets,
          {
            presets: tempProfiles,
            printer: this.printer,
          },
          {
            title: `${this.$i18next.t('Temperature Presets')}`,
            confirmButtonText: 'Apply',
            showCancelButton: true,
            preConfirm: () => {
              return {
                preset: document.getElementById('selected-preset').value,
              }
            },
          }
        )
        .then((result) => {
          if (result.value?.preset) {
            this.applyTempPreset(result.value.preset)
          }
        })
    },
    applyTempPreset(preset) {
      const tempProfiles = get(this.printer, 'settings.temp_profiles', [])
      let profile = tempProfiles.find((p) => p.name === preset)

      const presetObj = {}

      if (!profile) {
        if (preset === 'OFF') {
          presetObj.bed = 0
          presetObj.extruder = 0
          presetObj.chamber = 0
        } else {
          return
        }
      } else {
        Object.entries(profile).forEach((p) => {
          const presetName = p[0]
          if (presetName.toLowerCase().includes('bed')) {
            presetObj.bed = p[1]
          } else if (
            presetName.toLowerCase().includes('tool') ||
            presetName.toLowerCase().includes('extruder')
          ) {
            presetObj.extruder = p[1]
          } else if (presetName.toLowerCase().includes('chamber')) {
            presetObj.chamber = p[1]
          }
        })
      }

      const temperatures = get(this.printer, 'status.temperatures', [])
      Object.entries(temperatures).forEach((t) => {
        const toolName = t[0]
        if (toolName.toLowerCase().includes('bed')) {
          this.handleSetTemp(toolName, presetObj.bed)
        } else if (
          toolName.toLowerCase().includes('tool') ||
          toolName.toLowerCase().includes('extruder')
        ) {
          this.handleSetTemp(toolName, presetObj.extruder)
        } else if (toolName.toLowerCase().includes('chamber') && presetObj.chamber) {
          this.handleSetTemp(toolName, presetObj.chamber)
        }
      })
    },
    handleSetTemp(name, temp) {
      this.printerComm.passThruToPrinter({
        func: 'set_temperature',
        target: '_printer',
        args: [name, temp],
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
</style>
