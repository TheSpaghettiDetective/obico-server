<template>
  <div>
    <span v-if="!valid && !printing">-</span>
    <b-spinner v-if="!valid && printing" small type="grow" label="Calculating..."></b-spinner>
    <span v-if="valid && showHours"
      >&nbsp;{{ hours }}<span class="text-subscript text-muted">h</span></span
    >
    <span v-if="valid && showMinutes"
      >&nbsp;{{ minutes }}<span class="text-subscript text-muted">m</span></span
    >
    <span v-if="valid && showSeconds"
      >&nbsp;{{ seconds }}<span class="text-subscript text-muted">s</span></span
    >
  </div>
</template>

<script>
export default {
  name: 'DurationBlock',
  props: {
    valid: {
      type: Boolean,
      required: true,
    },
    printing: {
      type: Boolean,
      required: true,
    },
    hours: {
      type: Number,
      default() {
        return 0
      },
    },
    showHours: {
      type: Boolean,
      default() {
        return false
      },
    },
    minutes: {
      type: Number,
      default() {
        return 0
      },
    },
    showMinutes: {
      type: Boolean,
      default() {
        return false
      },
    },
    seconds: {
      type: Number,
      default() {
        return 0
      },
    },
    showSeconds: {
      type: Boolean,
      default() {
        return false
      },
    },
  },
}
</script>
