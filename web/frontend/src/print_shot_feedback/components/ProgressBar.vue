<template>
  <div class="progress" style="height: 5px;">
    <div class="progress-bar" :class="{'bg-success': value === 100}" role="progressbar" :style="{width: valuePercent}" :aria-valuenow="value" aria-valuemin="0" aria-valuemax="100"></div>
  </div>
</template>

<script>
export default {
  name: "ProgressBar",
  props: {
    max: {
      default() {return 100},
      type: Number
    },
    value: {
      required: true,
      type: Number
    },
  },
  computed: {
    valuePercent() {
      return `${this.value}%`
    }
  }
}
</script>

<style>
 .progress-bar {
    justify-content: center;
    overflow: hidden;
    border-radius: 9999px;
 }
</style>
