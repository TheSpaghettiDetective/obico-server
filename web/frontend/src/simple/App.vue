<template>
  <div>
    <div class="example">{{ msg }}</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      msg: "Hello from vue!"
    };
  }
};
</script>

<style lang="sass">
@import "../main/main.sass"

.example
  color: $primary
</style>
