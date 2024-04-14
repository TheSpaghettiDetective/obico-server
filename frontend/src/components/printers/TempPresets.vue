<template>
  <div>
    <div>
      <h5>{{ $t("Presets") }}:</h5>
    </div>
    <div>
      <b-form-select id="id_preset" v-model="currentPreset" class="form-control">
        <b-form-select-option v-for="pre in allPresets" :key="pre.name" :value="pre.name">
          {{ pre.name }}
        </b-form-select-option>
      </b-form-select>
    </div>

    <muted-alert class="mt-4 mb-1">
      {{ $t('Temperature presets can be edited or added in {agentName} settings.',{agentName}) }}
      
    </muted-alert>

    <input id="selected-preset" v-model="currentPreset" type="hidden" />
  </div>
</template>

<script>
import MutedAlert from '@src/components/MutedAlert.vue'

export default {
  name: 'TempPresets',

  components: {
    MutedAlert,
  },

  props: {
    presets: {
      type: Array,
      required: true,
    },
    printer: {
      type: Object,
      required: true,
    },
  },

  data: function () {
    return {
      currentPreset: null,
    }
  },

  computed: {
    allPresets() {
      let presets = [...this.presets]
      presets.push({ value: 0, name: 'OFF' })
      return presets
    },
    agentName() {
      return this.printer.agentDisplayName()
    },
  },

  mounted() {
    this.currentPreset = this.allPresets[0].name
  },

  methods: {},
}
</script>
<style></style>
