<template>
  <div class="progress">
    <div
      class="progress-bar"
      role="progressbar"
      :class="{'bg-success': value === 100}"
      :style="{width: `${this.value}%`}"
      :aria-valuenow="value"
      aria-valuemin="0"
      aria-valuemax="100"
    >{{ displayedValuePercent }}</div>
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
    displayedValuePercent() {
      return this.value < 3 ? '' : `${this.value}%`;
    }
  }
};
</script>

<style  lang="sass" scoped>
@use "~main/theme"

.progress
  background-color: theme.$color-bg-dark
</style>
