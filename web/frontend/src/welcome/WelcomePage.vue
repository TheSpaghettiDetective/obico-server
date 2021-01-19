<template>
  <div class="row justify-content-center">
    <div class="col-sm-12 col-lg-10 wizard-container">
      <div class="container">
        <br />
        <div class="row">
          <h1 class="mx-auto">Welcome To</h1>
        </div>
        <div class="row">
          <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
            <img class="logo-img"
              :src="require('../../../app/static/img/logo-inverted.png')" />
          </div>
        </div>
        <hr />
        <div class="row">
          <h2 class="mx-auto pt-3 text-center">Your <span class="text-primary">30-Day Free Trial</span> Started Today!</h2>
        </div>
        <div class="row pt-2">
          <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
            <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">Premium 25fps Webcam Streaming</span></div>
            <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">Unlimited Print Hours Watched by The Detective</span></div>
            <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">G-Code Remote Upload and Printing</span></div>
            <div class="pb-1"><i class="feature-check fas fa-check-circle"></i><span class="feature-text">Unlimited Secure Tunneling to your Octoprint</span></div>
          </div>
        </div>
        <div class="row text-center mt-5">
          <div class="mx-auto lead">Link your OctoPrint now so that you can fully enjoy the 30-Day Free Trial!</div>
        </div>
        <div class="row p mt-4">
          <b-button href="/printers/wizard/" variant="primary" class="mx-auto py-3 btn">Link OctoPrint</b-button>
        </div>
        <div class="row">
          <div class="text-muted mx-auto text-center font-weight-light">It's as easy as 1-2-3.</div>
        </div>
        <div class="row mt-3">
          <b-button href="/printers/" variant="outline-primary text-white" class="mx-auto py-3 btn">Just Checking Out</b-button>
        </div>
        <div class="row">
          <div class="text-muted mx-auto text-center font-weight-light">Not a whole lot you can see without your OctoPrint linked.</div>
        </div>
        <div class="row py-2">
          <b-button @click="openOctoprint" variant="outline" class="mx-auto py-3 btn btn-link">Don't Have Octoprint?</b-button>
        </div>
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
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.wizard-container
  margin: 2em 0em
  padding: 1em
  background: theme.$body-bg
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important

.btn
  width: 240px
  height: 3rem
  font-size: 1rem
  line-height: 0.9rem

.btn-link
  color: theme.$white

hr
  background-color: theme.$white

.logo-img
  width: 100%

.feature-check
  color: theme.$primary

.feature-text
  margin-left: 0.5em

.success
  width: 12rem
</style>
