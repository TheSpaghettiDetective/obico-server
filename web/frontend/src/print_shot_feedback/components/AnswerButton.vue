<template>
  <div class="form-group">
    <button
      type="button"
      :class="classes"
      :disabled="disabled"
      @click="$emit('click')"
    >
      <i
        v-if="checked && !updating"
        class="fas fa-check"
      />
      <i
        v-if="updating"
        class="fas fa-spinner fa-spin"
      />
      <slot />
    </button>
  </div>
</template>

<script>
export default {
  name: "AnswerButton",
  props: {
    defaultClass: {
      default() {return "btn-primary"},
      type: String
    },
    checkedClass: {
      default() {return "btn-primary"},
      type: String
    },
    disabled: {
      default() {return false},
      type: Boolean
    },
    checked: {
      default() {return false},
      type: Boolean
    },
    updating: {
      default() {return false},
      type: Boolean
    },
  },
  computed: {
    classes() {
      if (this.checked) {
        return `btn ${this.checkedClass}`
      }
      return `btn ${this.defaultClass}`
    }
  }
};
</script>

<style></style>
