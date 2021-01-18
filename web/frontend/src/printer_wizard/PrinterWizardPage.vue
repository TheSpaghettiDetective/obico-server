<template>
<div class="row justify-content-center">
  <div class="col-sm-12 col-lg-10 wizard-container">
    <div v-if="setupStage === 'linkPrinter'">
      <form-wizard
        :color="theme.primary"
        step-size="sm"
      >
        <h2 slot="title">
          <img class="header-img"
            :src="require('../../../app/static/img/octo-inverted.png')" />
          Link OctoPrint
        </h2>
        <tab-content title="Install Plugin">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>Open OctoPrint in another browser tab. </li>
                  <li>OctoPrint settings menu > Plugin Manager > Get More... </li>
                  <li>Enter "The Spaghetti Detective" to search for the plugin. Click "Install".</li>
                  <li>After installing, Octoprint will restart (this may take a few minutes).</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img class="mx-auto" :src="require('@static/img/install_plugin.png')">
              </div>
            </div>
          </div>
        </tab-content>
        <tab-content title="Plugin Wizard">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>Upon restarting, <b>Access Anywhere - The Spaghetti Detective</b> wizard will popup.</li>
                  <li>Follow the instructions in the wizard.</li>
                  <li>Select <b>"Web Setup"</b> when asked.</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img class="mx-auto" :src="require('@static/img/plugin_wizard_websetup.png')">
              </div>
            </div>
          </div>
        </tab-content>
        <tab-content title="Enter Code">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8  d-flex flex-column align-items-center">
                  <input disabled ref="code" class="code-btn" :value="`${verificationCode}`"/>
                  <small class="mx-auto py-1 text-muted">(Ctrl-C/Cmd-C to copy the code)</small>
                  <div class="mx-auto pt-1 pb-4"><span class="text-muted">Code expires in </span>xxx minutes</div>
                <div class="lead">Enter the <strong>6-digit verification code</strong> in the plugin</div>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img :src="require('@static/img/TSDVerificationScreenshot.png')">
                <div class="helper mx-auto py-2"><a class="link font-weight-bold" @click="showVerificationCodeHelpModal">Can't find the page to enter the 6-digit code?</a></div>
              </div>
            </div>
          </div>
        </tab-content>

        <template slot="footer" slot-scope="props">
        <div class="wizard-footer-left">
            <wizard-button v-if="props.activeTabIndex > 0" @click.native="props.prevTab(); prevTab();" class="btn btn-link btn-back">&lt; Back</wizard-button>
          </div>
          <div class="wizard-footer-right">
            <wizard-button v-if="!props.isLastStep" @click.native="props.nextTab(); nextTab();" class="wizard-footer-right wizard-btn" :style="props.fillButtonStyle">Next &gt;</wizard-button>
          </div>
        </template>
      </form-wizard>
      <div class="row">
        <div class="helper col-sm-12 float-right">Need help? Check out the <a href="#">step-by-step set up guide</a>.</div>
      </div>
    </div>

    <div v-if="setupStage === 'preferences'" class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center">
      <h2 class="preferences-title">Printer Preferences</h2>

      <PrinterPreferences />

      <div class="footer text-center mt-2 mb-5">
        <div class="tip">TIP: You can change your notification preferences later by going to: Settings > User Preferences</div>
        <br>
        <b-button variant="primary" class="btn btn-primary btn-lg px-5">Let's Go!</b-button>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@lib/server_urls'
import { BButton } from 'bootstrap-vue'
import {WizardButton, FormWizard, TabContent} from 'vue-form-wizard'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
import theme from '../main/main.sass'
import PrinterPreferences from '../printers/PrinterPreferences'

export default {
  components: {
    BButton,
    FormWizard,
    TabContent,
    WizardButton,
    PrinterPreferences
  },

  data() {
    return {
      verificationCode: '',
      currentTime: Date.now(),
      expiryMoment: null,
      url: urls.verificationCode(),
      pauseAndNotify: true,
      dropdown: false,
      advancedSettings: {
        isHotendHeaterOff: true,
        isBedHeaterOff: false,
        retractFilamentBy: 6.5,
        liftExtruderBy: 2.5,
        sensitivity: '5',
      },
      counter: 0,
      theme: theme,
      setupStage: 'linkPrinter', // first - linkPrinter, then - preferences
    }
  },
  computed: {
    title() {
      return this.isRelink() ? 'Re-Link' : 'Link'
    },
    sensitivityText() {
      switch (this.advancedSettings.sensitivity) {
        case '1': case '2': case '3':
          return 'Low - I don\'t want a lot of false alarms. Only alert me when you are absolutely sure.'
        case '4': case '5': case '6':
          return 'Medium - A few false alarms won\'t bother me. But some well-disguised spaghetti will be missed.'
        case '7': case '8': case '9':
          return 'High - Hit me with all the false alarms. I want to catch as many failures as possible'
        default:
          return 'Medium - A few false alarms won\'t bother me. But some well-disguised spaghetti will be missed.'
      }
    }
  },
  created() {
    // setInterval(() => {
    //   this.currentTime = Date.now()
    // }, 5000)
  },
  mounted() {
    // this.getVerificationCode()
    // this.codeInterval = setInterval(() => {
    //   this.getVerificationCode()
    // }, 5000)
  },
  methods: {
    isRelink: function() {
      return !!this.$route.query.printer_id
    },
    /**
     * Functions prevTab() and nextTab() are used to remove .checked class from circle steps
     * following current step (.checked class isn't removed by default after clicking Back
     * button, which causes showiing logo inside furter steps, not only completed ones).
     */
    prevTab() {
      document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').classList.remove('checked')
    },
    nextTab() {
      document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').classList.add('checked')

      if (document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').id === 'step-PluginWizard1') {
        this.getVerificationCode()
        this.codeInterval = setInterval(() => {
          this.getVerificationCode()
        }, 5000)
      }
    },
    // copy() {
    //   const codeButton = this.$refs.code
    //   console.log(codeButton.value)
    //   codeButton.focus()
    //   codeButton.select()
    //   try {
    //     const successful = document.execCommand('copy')
    //     const msg = successful ? 'successful' : 'unsuccessful'
    //     console.log('Fallback: Copying text command was ' + msg)
    //   } catch (err) {
    //     console.error('Fallback: Oops, unable to copy', err)
    //   }
    // },
    getVerificationCode() {
      this.currentTime = Date.now()

      axios
        .get(this.url)
        .then((resp) => {
          if (resp.data) {
            if (resp.data) {
              console.log(resp.data)

              this.verificationCode = resp.data.code
              const expiryTime = resp.data.expired_at.replace(/-|:/g, '')

              this.expiryMoment = moment(expiryTime).format('x')
              if (this.currentTime > this.expiryMoment) {
                this.url += `${resp.data.id}/`
              }

              this.counter += 1
              if (this.counter === 10) {
                clearInterval(this.codeInterval)
                this.setupStage = 'preferences'
              }

              if (resp.data.printer) {
                clearInterval(this.codeInterval)
                this.setupStage = 'preferences'
              }
            }
          }
        })
    },
    showVerificationCodeHelpModal() {
      this.$swal.fire({
        title: 'Not Seeing Verification Code Page?',
        html: `<p>The 6-digit code needs to be entered in The Spaghetti Detective plugin in OctoPrint. There are a few reasons why you can't find this page:</p>
        <p><ul>
        <li style="margin: 10px 0;">You don't have the plugin installed or you haven't restarted OctoPrint after installation. Click <a href="/printers/wizard/">here</a> to walk through the process again.</li>
        <li style="margin: 10px 0;">The installed plugin is on a version earlier than 1.5.0. You need to upgrade the plugin to <b>1.5.0</b> or later.</li>
        <li style="margin: 10px 0;">If for some reason you can't upgrade the plugin, follow <a href="/printers/new/">the old process</a> to link OctoPrint.</li>
        <li style="margin: 10px 0;">Still no dice? Check out the step-by-step <a href="#">set up guide</a>.</li>
        </ul></p>`,
        customClass: {
          container: 'dark-backdrop',
        },
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.wizard-btn
  border-radius: 300px

.wizard-container
  margin: 2em 0em
  padding: 1em
  background: theme.$body-bg
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important

.container
  padding: 0

.header-img
  width: 1em
  height: 1em
  margin: 0 12px

.img-container
  background: darken(theme.$body-bg, 5)
  padding: 1rem
  text-align: center

img
  width: 100%
  max-width: 450px

.spacer
 width: 200px

.code-btn
  border-radius: 10px
  text-align: center
  width: 21rem
  height: 60px
  background-color: black
  border: black
  color: white
  font-size: 2rem
  font-weight: 500
  letter-spacing: 2px

.helper
  font-size: 0.8rem
  font-weight: 400
  text-align: center
  padding: 0 36px

li
  margin: 2px -35px


// Preferences page

.preferences-title
  width: 100%
  text-align: center
  margin-top: 50px
  margin-bottom: 36px

.footer .tip
  margin-bottom: 40px
  text-align: left
</style>

<style lang="sass">
// Unscoped styles to style plugin elements
@use "~main/theme"

// Step label (not active)
.wizard-container .vue-form-wizard .wizard-nav-pills > li:not(.active) > a > span
  color: theme.$white

// Adjust numbers in the circles (form steps)
.wizard-nav.wizard-nav-pills .wizard-icon-circle i
  position: relative
  right: 2px

// Show logo inside completed sorm step circles
.wizard-nav.wizard-nav-pills li:not(.active)
  .wizard-icon-circle.checked i
    display: none

  .wizard-icon-circle.checked:before
    $size: 30px
    content: ""
    display: block
    width: $size
    height: $size
    background-image: url("/static/img/logo-square.png")
    background-size: $size $size
    position: absolute
    top: calc(50% - #{$size / 2})
    left: calc(50% - #{$size / 2})
    bottom: calc(50% - #{$size / 2})
    right: calc(50% - #{$size / 2})
</style>
