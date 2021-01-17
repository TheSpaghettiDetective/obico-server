<template>
<div class="row justify-content-center">
  <div class="col-sm-12 col-lg-10 wizard-container">
    <form-wizard>
      <h2 slot="title">Link OctoPrint</h2>
      <tab-content title="Install Plugin">
        <div class="container">
          <div class="col"></div>
          <div class="d-flex flex-column col">
            <b-row class="pb-3 d-flex justify-content-center">
              <img :src="require('@static/img/install_plugin.png')">
            </b-row>
            <b-row class="text-center">
              <div class="mx-auto content">Octoprint Settings menu > Plugin Manager > Install new Plugin</div>
            </b-row>
            <b-row class="pb-3 text-center">
              <div class="mx-auto content">After installing, Octoprint will restart (this may take a few minutes)</div>
            </b-row>
          </div>
        </div>
      </tab-content>
      <tab-content title="Plugin Wizard">
        <div class="container">
          <div class="col"></div>
          <div class="d-flex flex-column col">
            <b-row class="pb-3 d-flex justify-content-center">
              <img :src="require('@static/img/plugin_wizard_websetup.png')">
            </b-row>
            <b-row class="text-center">
              <div class="mx-auto content">Once OctoPrint has come back up, The Spaghetti Detective wizard will popup.</div>
            </b-row>
            <b-row class="text-center">
              <div class="mx-auto content">Follow the steps in the wizard.</div>
            </b-row>
            <b-row class="text-center">
              <div class="mx-auto content">Select "Web Setup".</div>
            </b-row>
          </div>
        </div>
      </tab-content>
      <tab-content title="Enter Code">
        <div class="container">
          <div class="col"></div>
          <div class="d-flex flex-column col">
            <b-row class="d-flex justify-content-center">
              <div class="px-1">
                <input disabled ref="code" class="code-btn" :value="`${verificationCode}`"/>
              </div>
            </b-row>
            <b-row class="pt-1 text-center">
              <div class="mx-auto pb-3">{{ `*This code will expire in ${validityHours} hrs ${validityMins} mins` }}</div>
            </b-row>
            <b-row class="pt-1 d-flex flex-column text-center">
              <div class="mx-auto subtitle">Enter the 6-Digit verification Code in the Plugin</div>
            </b-row>
            <b-row class="pb-3 d-flex justify-content-center">
              <img :src="require('@static/img/TSDVerificationScreenshot.png')">
            </b-row>
            <b-row>
              <div class="helper mx-auto pb-1" v-b-tooltip.hover.html.v-primary.right="tooltipTitle">Don't know where to enter the code? ⓘ</div>
            </b-row>
          </div>
        </div>
      </tab-content>
    </form-wizard>
    <b-row>
      <div class="helper col-sm-12 float-right">*Need help? Check out the step-by-step <a href="#">set up guide</a></div>
    </b-row>
        <div v-if="false" class="container">
          <div class="col"></div>
          <div class="d-flex flex-column col">
            <b-row class="pt-3 text-center">
              <div class="mx-auto title pb-3">Printer Preferences</div>
            </b-row>
            <b-row class="pt-1 text-center d-flex flex-column align-items-start mx-auto prefs">
                <div class="subtitle pb-3">When a potential failure is detected:</div>
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
            </b-row>
            <b-row class="pt-4">
              <b-button variant="primary" class="mx-auto py-3 btn">Let's Go!</b-button>
            </b-row>
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
import {FormWizard, TabContent} from 'vue-form-wizard'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'

export default {
  components: {
    BButton,
    BFormRadio,
    BFormCheckbox,
    BFormInput,
    FormWizard,
    TabContent,
  },

  data() {
    return {
      setupStage: 'install',
      verificationCode: '',
      currentTime: Date.now(),
      expiryMoment: null,
      url: urls.verificationCode(),
      tooltipTitle: {
        title: '<div>You need the latest</div><div>version of TSD plugin</div>',
        html: true
      },
      pauseAndNotify: true,
      dropdown: false,
      advancedSettings: {
        isHotendHeaterOff: true,
        isBedHeaterOff: false,
        retractFilamentBy: 6.5,
        liftExtruderBy: 2.5,
        sensitivity: '5',
      },
      counter: 0
    }
  },
  computed: {
    validityHours() {
      if (this.expiryMoment) {
        return `0${Math.floor((this.expiryMoment - this.currentTime) / 3600000)}`.slice(-2)
      }
      return '-'
    },
    validityMins() {
      if (this.expiryMoment) {
        return `0${(Math.floor((this.expiryMoment - this.currentTime) / 60000) % 60)}`.slice(-2)
      }
      return '-'
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
    this.getStage()
    this.getVerificationCode()
    this.codeInterval = setInterval(() => {
      this.getVerificationCode()
    }, 5000)
  },
  methods: {
    getStage() {
      const params = new URLSearchParams(window.location.search)
      const stage = params.get('setup')
      if (stage) {
        this.setupStage = stage
      }
      console.log('Stage Set!')
    },
    toLinkStage() {
      this.setupStage = 'link'
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
    }
  }
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

img
  height: 40vh

.spacer
 width: 200px

.title
  font-size: 2.5rem
  font-weight: 800

.subtitle
  font-size: 1.5rem
  font-weight: 500

.btn
  width: 220px
  height: 60px
  font-size: 1.3rem
  line-height: 1.3rem

.code-btn
  border-radius: 10px
  text-align: center
  width: 25rem
  height: 60px
  background-color: black
  border: black
  color: white
  font-size: 2rem
  font-weight: 500
  letter-spacing: 2px

.copy-btn
  width: 90px

.content
  font-size: 1rem
  line-height: 1.2rem
  font-weight: 400

.helper
  font-size: 0.8rem
  font-weight: 400

::v-deep .custom-control-label
  font-size: 1.2rem

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
