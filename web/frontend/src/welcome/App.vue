<template>
  <div>
    <div class="d-flex flex-column">
      <b-row class="pt-5">
        <div class="mx-auto title pb-3">Welcome!</div>
      </b-row>
      <b-row>
        <div class="mx-auto content">You have successfully created your account</div>
      </b-row>
      <b-row class="pb-5 text-center">
        <div class="mx-auto content next">Next, let's link your first OctoPrint printer and get you started in 3 simple steps</div>
      </b-row>
      <b-row class="py-2">
        <b-button href="/quicksetup" variant="primary" class="mx-auto py-3 btn">Quick Setup</b-button>
      </b-row>
      <b-row class="py-2">
        <b-button href="/printers" variant="outline-primary text-white" class="mx-auto py-3 btn">Skip, Set Up Later</b-button>
      </b-row>
      <b-row class="py-2">
        <b-button @click="openOctoprint" variant="outline" class="mx-auto py-3 btn">Don't have Octoprint?</b-button>
      </b-row>
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

.main-container
  position: fixed
  top: 50%
  left: 50%
  transform: translate(-50%, -50%)

.title
  font-size: 4rem
  font-weight: 800

.btn
  width: 280px
  height: 60px
  font-size: 1.3rem
  line-height: 1.3rem

.content
  font-size: 1.5rem
  font-weight: 400

.next
  width: 80vw
  max-width: 500px
</style>
