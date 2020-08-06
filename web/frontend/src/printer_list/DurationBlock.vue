<template>
  <div>
    <span
      v-if="!valid && !printing"
      >-</span>
    <i
      v-if="!valid && printing"
      class="fa fa-spinner"></i>
    <span
      v-if="valid && showHours"
    >{{ hours }}<span class="text-subscript text-muted">h</span></span>
    <span
      v-if="valid && showMinutes"
    >{{minutes}}<span class="text-subscript text-muted">m</span></span>
    <span
      v-if="valid && showSeconds"
    >{{seconds}}<span class="text-subscript text-muted">s</span></span>
  </div>
</template>

<script>
export default {
  name: 'DurationBlock',
  props: {
    valid: {
      type: Boolean,
      required: true
    },
    printing: {
      type: Boolean,
      required: true
    },
    hours: {
      type: Number,
      default() {return 0}
    },
    showHours: {
      type: Boolean,
      default() {return false}
    },
    minutes: {
      type: Number,
      default() {return 0}
    },
    showMinutes: {
      type: Boolean,
      default() {return false}
    },
    seconds: {
      type: Number,
      default() {return 0}
    },
    showSeconds: {
      type: Boolean,
      default() {return false}
    },
  },
}
</script>
