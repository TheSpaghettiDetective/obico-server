<template>
  <div class="btn-group btn-group-toggle" data-toggle="buttons">
    <label class="btn" v-for="(opt, index) in options" :key="index">
      <input type="radio" autocomplete="off" />
      {{ opt }}
    </label>
  </div>
</template>

<script>
export default {
  name: "RadioGroup",
  props: {
    options: Array,
    initChecked: Number
  },
  methods: {
    onTimeUpdate(event) {
      this.$emit("timeupdate", event.currentTime() / event.duration());
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.btn-group-toggle
  background: $body-bg
  border-radius: 300px
  .btn
    border: solid thin darken(white, 60)
</style>
