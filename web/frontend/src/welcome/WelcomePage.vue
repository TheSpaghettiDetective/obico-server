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
          <h2 class="mx-auto pt-3 text-center">Your <span class="text-primary">30-Day Free Trial</span> Starts Today!</h2>
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
        <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center">
          <div class="mt-4">
            <a href="/printers/wizard/" class="btn btn-primary btn-block mx-auto btn-lg">Link OctoPrint</a>
          </div>
          <div>
            <div class="text-muted mx-auto text-center font-weight-light">It's as easy as 1-2-3.</div>
          </div>
          <div class="mt-3">
            <a href="/printers/" class="btn btn-outline-secondary btn-block mx-auto">Just Checking Out</a>
          </div>
          <div>
            <div class="text-muted mx-auto text-center font-weight-light">Not a whole lot you can see without your OctoPrint linked.</div>
          </div>
          <div class="py-2">
            <button @click="openOctoprint" variant="outline" class="btn btn-block mx-auto btn-link">Don't Have Octoprint?</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
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
