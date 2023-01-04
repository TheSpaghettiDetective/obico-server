<template>
  <div class="py-2">
    <div class="row text-muted">
      <div class="col-2">
        <i class="fas fa-thermometer-half fa-lg"></i>
      </div>
      <small class="col-5"> Actual </small>
      <small class="col-5"> Target </small>
    </div>
    <div v-for="(item, key) in temperatures" :key="key" class="row">
      <div class="col-2 numbers">
        <span class="text-subscript text-muted">{{ temperatureDisplayName(key) }}</span>
      </div>
      <div class="col-5 numbers">
        {{ parseFloat(item.actual).toFixed(1) }}<span class="text-subscript text-muted">°C</span>
      </div>
      <div v-if="isEditable(item)" class="col-5 numbers" @click="onEditClicked(key, item)">
        {{ Math.round(item.target) }}<span class="text-subscript text-muted">°C</span>
        <span v-if="editable"
          >&nbsp;<i class="fas fa-pencil-alt" style="font-size: 0.6em"></i
        ></span>
      </div>
      <div v-else class="col-5 numbers">-</div>
    </div>
  </div>
</template>

<script>
import { temperatureDisplayName } from '@src/lib/utils'

export default {
  name: 'StatusTemp',
  props: {
    temperatures: {
      type: Object,
      required: true,
    },
    editable: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    onEditClicked(key, item) {
      if (this.editable) {
        this.$emit('TempEditClicked', key, item)
      }
    },
    isEditable(temperature) {
      // "target === null" means it's only a sensor, not a heater.
      return temperature.target !== null
    },
    temperatureDisplayName: temperatureDisplayName,
  },
}
</script>
