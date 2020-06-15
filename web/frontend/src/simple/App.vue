<template>
  <div>
    <div class="example">
      {{ msg }}
    </div>
    <div>
      <img :src="logo">
      <img :src="require('./assets/logo.png')">
      <img :src="require('../../../app/static/img/logo.png')">
    </div>
  </div>
</template>

<script>
import logo from "./assets/logo.png"

export default {
  data() {
    return {
      msg: "Hello from vue!",
      logo: logo,
    };
  }
};
</script>

<style lang="sass">
@import "../main/main.sass"

img
  width: 200px
  display: block

.example
  color: $primary
</style>
