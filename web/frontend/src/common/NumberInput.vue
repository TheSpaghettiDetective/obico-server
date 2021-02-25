<template>
  <div class="input-group input-group-sm input-wrapper">
    <div class="input-group-prepend">
      <button
        class="btn btn-outline-secondary control-button"
        type="button"
        @click="
          value = value > 0 ? Math.round((value - step) * 10) / 10 : 0;
          $emit('change-value', value);
        "
        :disabled="disable"
      >↓</button>
    </div>
    <input
      type="text"
      class="form-control text-center field_required"
      disabled
      aria-describedby="basic-addon1"
      :value="value + ' mm'"
      :style="{opacity: disable ? .3 : 1}">
    <div class="input-group-append">
      <button
        class="btn btn-outline-secondary control-button"
        type="button"
        @click="
          value = Math.round((value + step) * 10) / 10;
          $emit('change-value', value);
        "
        :disabled="disable"
      >↑</button>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NumberInput',

    props: {
      value: {
        type: Number,
        default: 0
      },
      step: {
        type: Number,
        default: 0.5
      },
      disable: {
        type: Boolean,
        default: false
      },
    },
  }
</script>

<style lang="sass" scoped>
  @use "~main/theme"

  .input-group.input-wrapper
    .control-button
      border-width: 1px

    input
      border-top-color: theme.$white
      border-bottom-color: theme.$white
      color: theme.$white
      width: 5rem
</style>