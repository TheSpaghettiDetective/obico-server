<template>
  <div>
    <div class="d-flex flex-column">
      <b-row class="mx-auto pt-4">
        <img :src="require('@static/img/16JanWelcomeSuccessIcon.png')" class="success">
      </b-row>
      <b-row>
        <div class="mx-auto title pb-3">Success!</div>
      </b-row>
      <b-row class="text-center">
        <div class="mx-auto content">Link your Octoprint printer now in 3 simple steps to enjoy the benefits of your <strong>30-day free trial</strong>, on us!</div>
      </b-row>
      <b-row class="pt-3 text-center d-flex flex-column align-items-start mx-auto">
        <div class="pb-1 small-text"><img :src="require('@static/img/Tick-14.png')" class="tick mr-1">Enhanced 25fps Webcam Streaming</div>
        <div class="pb-1 small-text"><img :src="require('@static/img/Tick-14.png')" class="tick mr-1">Unlimited Monitoring of Your Prints by The Spaghetti Detective</div>
        <div class="pb-3 small-text"><img :src="require('@static/img/Tick-14.png')" class="tick mr-1">Unlimited Remote Tunneling to your Octoprint anytime, anywhere</div>
      </b-row>
      <b-row class="py-2">
        <b-button href="/printers/new?setup=install" variant="primary" class="mx-auto py-3 btn">Link Printer</b-button>
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

.tick
  width: 1rem
</style>
