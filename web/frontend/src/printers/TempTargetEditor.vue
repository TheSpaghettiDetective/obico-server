<template>
  <div>
    <div class="text-center">
      <h1
        v-if="value > 0"
        class="target-temp-degree"
      >{{ value }} <span class="text-subscript text-muted">°C</span></h1>
      <h1
        v-if="value < 1"
        class="target-temp-degree"
      >OFF</h1>
    </div>
    <br />
    <div class="mb-5">
      <div>
        <h5>Presets:</h5>
      </div>
      <div>
        <b-form-select v-model="preset" id="id_preset" @change="onPresetChanged">
          <b-form-select-option
            v-for="pre in allPresets"
            :key="pre.value"
            :value="parseInt(pre.value)">
            {{pre.title}}
          </b-form-select-option>
        </b-form-select>
      </div>
      <br />
      <h5>Manual:</h5>
      <div>
        <vue-slider
          :min="0"
          :max="maxTemp"
          :step="1"
          :tooltip="'none'"
          v-model="value"
          @change="onSliderChanged"
        ></vue-slider>
        <input
          id="target-temp"
          v-model="value"
          type="hidden"
        >
      </div>
    </div>
  </div>
</template>

<script>
import VueSlider from 'vue-slider-component'

export default {
  name: 'TempTargetEditor',
  components: {
    VueSlider,
  },
  props: {
    presets: {
      type: Array,
      required: true
    },
    maxTemp: {
      type: Number,
      required: true
    },
    curTarget: {
      type: Number,
      required: true,
    },
  },
  data() {
    let curPreset = this.presets.find((pre) => pre.target == this.curTarget) || {target: this.curTarget != 0 ? -1 : 0}
    return {value: this.curTarget, preset: curPreset.target}
  },
  computed: {
    allPresets() {
      let presets = []
      presets.push({value: -1, title: 'Manual'})
      presets.push({value: 0, title: 'OFF'})
      this.presets.forEach((pre) => {
        presets.push(
          {value: pre.target, title: `${pre.name} (${pre.target}°C)`})
      })
      return presets
    }
  },
  methods: {
    onPresetChanged() {
      if (this.preset > -1) {
        this.value = this.preset
      }
    },
    onSliderChanged() {
      if (this.value == 0) {
        this.preset = 0
      } else {
        this.preset = -1
      }

    }
  }
}
</script>
<style>
</style>
