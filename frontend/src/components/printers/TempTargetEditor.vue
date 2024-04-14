<template>
  <div>
    <div class="text-center">
      <h1 v-if="value > 0" class="target-temp-degree">
        {{ value }} <span class="text-subscript text-muted">°C</span>
      </h1>
      <h1 v-if="value < 1" class="target-temp-degree">{{ $t("OFF") }}</h1>
    </div>
    <br />
    <div class="mb-5">
      <div>
        <h5>{{ $t("Presets") }}:</h5>
      </div>
      <div>
        <b-form-select
          id="id_preset"
          v-model="preset"
          class="form-control"
          @change="onPresetChanged"
        >
          <b-form-select-option
            v-for="pre in allPresets"
            :key="pre.name"
            :value="parseInt(pre.value)"
          >
            {{ pre.title }}
          </b-form-select-option>
        </b-form-select>
      </div>
      <br />
      <h5>{{ $t("Manual") }}:</h5>
      <div>
        <slider-input
          v-model="value"
          :min="0"
          :max="maxTemp"
          :step="1"
          @change="onSliderChanged"
        ></slider-input>
        <input id="target-temp" v-model="value" type="hidden" />
      </div>
    </div>
  </div>
</template>

<script>
import SliderInput from '@src/components/SliderInput.vue'

export default {
  name: 'TempTargetEditor',
  components: {
    SliderInput,
  },
  props: {
    presets: {
      type: Array,
      required: true,
    },
    maxTemp: {
      type: Number,
      required: true,
    },
    curTarget: {
      type: Number,
      required: true,
    },
  },
  data() {
    let curPreset = this.presets.find((pre) => pre.target == this.curTarget) || {
      target: this.curTarget != 0 ? -1 : 0,
    }
    return { value: this.curTarget, preset: curPreset.target }
  },
  computed: {
    allPresets() {
      let presets = []
      presets.push({ value: -1, title: 'Manual', name: 'manual' })
      presets.push({ value: 0, title: 'OFF', name: 'off' })
      this.presets.forEach((pre) => {
        if (pre.target) {
          presets.push({
            value: pre.target,
            name: pre.name,
            title: `${pre.name} (${pre.target}°C)`,
          })
        }
      })
      return presets
    },
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
    },
  },
}
</script>
<style></style>
