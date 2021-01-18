<template>
<div class="row justify-content-center">
  <div class="col-sm-12 col-lg-10 wizard-container">
    <form-wizard
      :color="theme.primary"
      step-size="sm"
    >
      <h2 slot="title"><i class="fas fa-link mr-3" />Link OctoPrint</h2>
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
           <wizard-button v-if="props.activeTabIndex > 0" @click.native="props.prevTab()" class="btn btn-link" :style="props.fillButtonStyle">&lt; Back</wizard-button>
        </div>
        <div class="wizard-footer-right">
          <wizard-button v-if="!props.isLastStep" @click.native="props.nextTab()" class="wizard-footer-right wizard-btn" :style="props.fillButtonStyle">Next &gt;</wizard-button>
        </div>
      </template>
    </form-wizard>
    <div class="row">
      <div class="helper col-sm-12 float-right">Need help? Check out the <a href="#">step-by-step set up guide</a>.</div>
    </div>
        <div v-if="false" class="container">
          <div class="col"></div>
          <div class="d-flex flex-column col">
            <div class="row pt-3 text-center">
              <div class="mx-auto pb-3">Printer Preferences</div>
            </div>
            <div class="row pt-1 text-center d-flex flex-column align-items-start mx-auto prefs">
                <div class="pb-3">When a potential failure is detected:</div>
                <b-form-radio :v-model="!pauseAndNotify" name="notify" size="lg" class="notify">Just notify me</b-form-radio>
                <b-form-radio :v-model="pauseAndNotify" name="notify" size="lg" class="notify pb-4">Pause the printer and notify me</b-form-radio>
                <div class="settings d-flex justify-content-between" @click="dropdown = !dropdown">
                  <div class="px-2">Advanced Settings</div>
                  <div class="px-2"></div>
                  <div v-if="!dropdown" class="px-2"> ></div>
                  <div v-else class="px-2">&lt;</div>
                </div>
                <div v-if="!dropdown">TIP: You can change your notification preferences later by going to:Settings > UserPreferences</div>
                <div v-else class="d-flex flex-column align-items-start">
                  <div class="px-2 warning">⚠ If you are not sure about the settings below, leave the default values to minimize surprises</div>
                  <div class="subheading pt-2">When print is paused:</div>
                  <b-form-checkbox v-model="advancedSettings.isHotendHeaterOff">Turn off hotend heater(s)</b-form-checkbox>
                  <b-form-checkbox v-model="advancedSettings.isBedHeaterOff">Turn off bed heater</b-form-checkbox>
                  <div class="d-flex align-items-center">
                    <div class="col input-label-text">Retract filament by</div>
                    <b-form-input v-model="advancedSettings.retractFilamentBy" placeholder="6.5"></b-form-input>
                    <input disabled ref="code" class="mm" value="mm"/>
                  </div>
                  <div class="d-flex align-items-center">
                    <div class="col input-label-text">Lift extruder by</div>
                    <b-form-input v-model="advancedSettings.liftExtruderBy"></b-form-input>
                    <input disabled ref="code" class="mm" value="mm"/>
                  </div>
                  <div class="subheading pt-2">How sensitive do you want the Detective to be on this printer?</div>
                  <b-form-input v-model="advancedSettings.sensitivity" type="range" min="1" max="9"></b-form-input>
                  <div>{{ sensitivityText }}</div>
                </div>
            </div>
            <div class="row pt-4">
              <b-button variant="primary" class="mx-auto py-3 btn">Let's Go!</b-button>
            </div>
          </div>
        </div>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@lib/server_urls'
import { BButton, BFormRadio, BFormCheckbox, BFormInput } from 'bootstrap-vue'
import {WizardButton, FormWizard, TabContent} from 'vue-form-wizard'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
import theme from '../main/main.sass'

export default {
  components: {
    BButton,
    BFormRadio,
    BFormCheckbox,
    BFormInput,
    FormWizard,
    TabContent,
    WizardButton
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
      theme: theme
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
    setInterval(() => {
      this.currentTime = Date.now()
    }, 5000)
  },
  mounted() {
    this.getVerificationCode()
    this.codeInterval = setInterval(() => {
      this.getVerificationCode()
    }, 5000)
  },
  methods: {
    isRelink: function() {
      return !!this.$route.query.printer_id
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
      if (this.setupStage === 'link') {
        axios
        .get(this.url)
        .then((resp) => {
          if (resp.data) {
            this.verificationCode = resp.data.code
            const expiryTime = resp.data.expired_at.replace(/-|:/g, '')
            this.expiryMoment = moment(expiryTime).format('x')
            console.log(resp.data)
            if (this.currentTime > this.expiryMoment) {
              this.url += `${resp.data.id}`
            }
            this.counter += 1
            if (this.counter === 10) {
              clearInterval(this.codeInterval)
              this.setupStage = 'preferences'
            }
            // if (resp.data.printer) {
            //   clearInterval(this.codeInterval)
            //   this.setupStage = 'preferences'
            // }
          }
        })
      }
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

// Preferences page.

.settings
  background-color: #616a7a
  width: 100%

.prefs
  max-width: 500px

.warning
  color: #d9a821

.subheading
  color: gray

.mm
  width: 40px
  text-align: center
  height: calc(1.5em + 0.75rem + 2px)

.input-label-text
  min-width: 170px
</style>

<style lang="sass">
// Unscoped styles to style plugin elements
@use "~main/theme"

.wizard-container .vue-form-wizard .wizard-nav-pills > li:not(.active) > a > span
  color: theme.$white
</style>
