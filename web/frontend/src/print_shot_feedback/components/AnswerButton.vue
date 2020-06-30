<template>
  <div class="form-group">
    <button type="button" :class="classes" :disabled="disabled" @click="$emit('click')">
      <i v-if="checked && !updating" class="fas fa-check px-2" />
      <slot />
      <i v-if="updating" class="fas fa-spinner fa-spin mx-2" />
    </button>
  </div>
</template>

<script>
export default {
  name: 'AnswerButton',
  props: {
    defaultClass: {
      default() {
        return 'btn-secondary'
      },
      type: String
    },
    checkedClass: {
      default() {
        return 'btn-secondary'
      },
      type: String
    },
    disabled: {
      default() {
        return false
      },
      type: Boolean
    },
    checked: {
      default() {
        return false
      },
      type: Boolean
    },
    updating: {
      default() {
        return false
      },
      type: Boolean
    }
  },
  computed: {
    classes() {
      if (this.checked) {
        return `btn btn-block ${this.checkedClass}`
      }
      return `btn btn-block ${this.defaultClass}`
    }
  }
}
</script>

<style></style>
