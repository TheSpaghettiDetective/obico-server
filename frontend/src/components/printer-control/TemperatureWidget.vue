<template>
  <widget-template>
    <template #title>Temperature Controls</template>
    <template #content>
      <slot name="content">
        <div class="wrapper">
          <template v-if="show">
            <temperature-item
              v-for="(item, key) in temperatures"
              :key="key"
              :temp-key="key"
              :temp-item="item"
              :editable="editable"
              @TempEditClicked="onEditClicked(key, item)"
            />
          </template>
          <template v-else>
            <div class="text-center mt-4">
              <b-spinner></b-spinner>
              <p class="mt-2">Loading temperature...</p>
            </div>
          </template>
        </div>
      </slot>
    </template>
  </widget-template>
</template>

<script>
import TempTargetEditor from '@src/components/printers/TempTargetEditor.vue'
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
    editable() {
      // If temp_profiles is missing, it's a plugin version too old to change temps
      return get(this.printer, 'settings.temp_profiles') != undefined
    },
    show() {
      return Object.keys(this.temperatures).length >= 2
    },
  },

  methods: {
    temperatureDisplayName,
    onEditClicked(key, item) {
      if (!this.editable) {
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
            this.printerComm.passThruToPrinter({
              func: 'set_temperature',
              target: '_printer',
              args: [key, targetTemp],
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
</style>
