<template>
  <div>
    <div class="d-flex flex-column">
      <div class="row">
        <div class="mx-auto title pb-3">Success!</div>
      </div>
      <div class="row text-center">
        <div class="mx-auto content">Link your Octoprint printer now in 3 simple steps to enjoy the benefits of your <strong>30-day free trial</strong>, on us!</div>
      </div>
      <div class="row pt-3 text-center d-flex flex-column align-items-start mx-auto">
        <div class="pb-1 small-text">Enhanced 25fps Webcam Streaming</div>
        <div class="pb-1 small-text">Unlimited Monitoring of Your Prints by The Spaghetti Detective</div>
        <div class="pb-3 small-text">Unlimited Remote Tunneling to your Octoprint anytime, anywhere</div>
      </div>
      <div class="row py-2">
        <b-button href="/printers/wizard/?setup=install" variant="primary" class="mx-auto py-3 btn">Link Printer</b-button>
      </div>
      <div class="row py-2">
        <b-button href="/printers/" variant="outline-primary text-white" class="mx-auto py-3 btn">Skip, Set Up Later</b-button>
      </div>
      <div class="row py-2">
        <b-button @click="openOctoprint" variant="outline" class="mx-auto py-3 btn">Don't have Octoprint?</b-button>
      </div>
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
  },
  beforeCreate: function() {
    document.body.className = 'solid-bg'
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
  font-size: 3rem
  font-weight: 800

.btn
  width: 240px
  height: 3rem
  font-size: 1rem
  line-height: 0.9rem

.content
  font-size: 1rem
  line-height: 1.5rem
  font-weight: 400
  width: 60vw
  max-width: 380px

.small-text
  font-size: 0.75rem

.success
  width: 12rem
</style>
