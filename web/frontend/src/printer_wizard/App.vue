<template>
  <div>
    <div class="container">
      <div class="col"></div>
      <div class="d-flex flex-column col">
        <b-row class="pt-3 text-center">
          <div class="mx-auto title pb-3">Install TSD Plugin in the Octoprint Store</div>
        </b-row>
        <b-row class="pb-3 d-flex justify-content-center">
          <img :src="require('@static/img/TSDInstallScreenshot.png')">
        </b-row>
        <b-row class="text-center">
          <div class="mx-auto content">Octoprint Settings menu > Plugin Manager > Install new Plugins</div>
        </b-row>
        <b-row class="pb-3 text-center">
          <div class="mx-auto content">After installing, Octoprint will restart (this may take a few minutes)</div>
        </b-row>
        <b-row class="pt-2">
          <b-button @click="openOctoprint" variant="primary" class="mx-auto py-3 btn">Next</b-button>
        </b-row>
      </div>
      <div class="helper col ml-auto">*Need help? Check out the step by step <a href="#">set up guide</a></div>
    </div>
  </div>
</template>

<script>
import { BButton } from 'bootstrap-vue'

export default {
  components: {
    BButton
  },
  data() {
    return {
    }
  },
  methods: {
    openOctoprint() {
      window.open('https://octoprint.org/download')
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

img
  width: 35vw
  min-width: 360px

.spacer
 width: 200px

.title
  font-size: 2.5rem
  font-weight: 800

.btn
  width: 220px
  height: 60px
  font-size: 1.3rem
  line-height: 1.3rem

.content
  font-size: 1.2rem
  font-weight: 400

.helper
  font-size: 0.8rem
  font-weight: 400
  max-width: 200px
</style>
