<template>
  <div class="progress">
    <div
      class="progress-bar"
      role="progressbar"
      :class="{'bg-success': value === 100}"
      :style="{width: valuePercent}"
      :aria-valuenow="value"
      aria-valuemin="0"
      aria-valuemax="100"
    >{{ valuePercent }}</div>
  </div>
</template>

<script>
export default {
  name: "ProgressBar",
  props: {
    max: {
      default() {
        return 100;
      },
      type: Number
    },
    value: {
      required: true,
      type: Number
    }
  },
  computed: {
    valuePercent() {
      return `${this.value}%`;
    }
  }
};
</script>

<style  lang="sass" scoped>
@use "~main/theme"

.progress
  background-color: theme.$color-bg-dark
</style>
