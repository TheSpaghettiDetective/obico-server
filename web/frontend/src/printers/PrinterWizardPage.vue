<template>
<div class="row justify-content-center">
  <pull-to-reveal>
    <navbar view-name="app.views.web_views.edit_printer"></navbar>
  </pull-to-reveal>

  <div class="col-sm-12 col-lg-10 wizard-container form-container" :class="{'logo-bg': verifiedPrinter }">

    <div v-if="verifiedPrinter" class="text-center py-5">
      <svg class="success-checkmark" viewBox="0 0 446 410" xmlns="http://www.w3.org/2000/svg">
        <path d="M173.26 409.06C77.84 409.06 0.200012 331.43 0.200012 236C0.200012 140.57 77.84 62.94 173.26 62.94C268.68 62.94 346.32 140.57 346.32 236C346.32 331.43 268.69 409.06 173.26 409.06ZM173.26 86.06C90.59 86.06 23.33 153.32 23.33 235.99C23.33 318.66 90.59 385.92 173.26 385.92C255.93 385.92 323.19 318.67 323.19 236C323.19 153.33 255.93 86.07 173.26 86.07V86.06Z" />
        <path d="M173.26 293.77L95.82 216.34L117.04 195.12L173.26 251.35L424 0.600006L445.22 21.81L173.26 293.77Z" />
      </svg>

      <h3 class="pb-4">Successfully linked to your account!</h3>
      <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center">
        <saving-animation :errors="errorMessages.printer_name" :saving="saving.printer_name">
          <div class="printer-name-input">
            <div class="edit-icon">
              <i class="fas fa-pen"></i>
            </div>
            <input
              type="text"
              class="dark"
              placeholder="Printer name"
              v-model="verifiedPrinter.name"
              @input="updatePrinterName"
            >
          </div>
        </saving-animation>
        <div>
          <div class="text-muted mx-auto text-center font-weight-light">Give your printer a shiny name.</div>
        </div>
      </div>
      <br /><br />
      <div class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center">
        <div class="mt-4">
          <a href="/printers/" class="btn-primary btn-block mx-auto btn btn-lg">Go Check Out Printer Feed!</a>
        </div>
        <div class="mt-5">
          <a href="/user_preferences/" class="btn btn-outline-secondary btn-block mx-auto btn">Add Phone Number</a>
        </div>
        <div>
          <div class="text-muted mx-auto text-center font-weight-light">Receive text (SMS) in case of print failures.</div>
        </div>
        <div class="mt-4">
          <a :href="editPrinterUrl" class="btn btn-outline-secondary btn-block mx-auto btn">Change Printer Settings</a>
        </div>
        <div>
          <div class="text-muted mx-auto text-center font-weight-light">You can always change it later.</div>
        </div>
      </div>
    </div>

    <div v-else>
      <form-wizard
        color="rgb(var(--color-primary))"
        step-size="sm"
      >
        <h2 slot="title">
          <svg class="header-img"  viewBox="0 0 165 152" xmlns="http://www.w3.org/2000/svg">
            <path class="tone-1" d="M162.703 74.7397C162.703 74.6597 162.643 74.5297 162.573 74.3397C161.403 70.4597 153.253 43.7297 132.123 32.7997C110.123 21.4397 81.0226 16.9397 53.2126 46.3497C17.3626 84.2697 57.8826 125.68 61.1726 151.06H16.1726C-4.90742 111.25 -2.72743 75.1097 7.69257 50.4797C20.1726 21.0897 62.1726 -8.60031 105.753 2.30969C180.713 21.0697 162.703 74.7397 162.703 74.7397Z" />
            <path class="tone-2" d="M163 72.8212C162.526 71.6245 161.887 69.9878 161.29 68.8218C160.945 67.9524 160.552 67.1022 160.115 66.2748C160.115 66.2748 159.796 65.436 159.785 65.4258C156.88 60.608 154.871 56.5165 150.275 52.6705C146.377 49.3988 142.103 46.597 137.541 44.3238C136.974 44.0374 136.407 43.7509 135.841 43.5055C119.17 35.6804 98.5736 34.2279 80.9447 43.7816C59.926 55.1868 61.8527 72.4223 68.7456 86.3028V86.3846C70.6573 90.1567 72.9056 93.7511 75.4633 97.1249C75.4633 97.1249 75.4633 97.1249 75.4633 97.1249C77.1521 99.3968 78.9648 101.575 80.8932 103.651C88.3321 111.609 95.1529 125.622 99.8306 136.68C102.468 142.929 104.426 148.248 105.384 151H59.823C59.8326 150.963 59.8326 150.924 59.823 150.887C58.5144 125.847 14.9522 83.674 51.704 45.0807C79.5228 15.9081 108.599 20.3679 130.565 31.6298C151.625 42.4519 161.475 68.4535 162.887 72.4121C162.938 72.6064 162.969 72.7599 163 72.8212Z" />
          </svg>
          {{title}}
        </h2>
        <tab-content v-if="printerIdToLink" title="Open Plugin Settings">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <div class="text-warning">
                  Warning: Re-Linking OctoPrint should be your last resort to solve issues. Please make sure you have exhausted all options on <a href="https://www.thespaghettidetective.com/help/">TSD's help website</a>.
                </div>
                <ol>
                  <li>Open OctoPrint in another browser tab. </li>
                  <li>Select <em>"OctoPrint settings menu → Access Anywhere - The Spaghetti Detective"</em>.</li>
                  <li>Select <em>"Troubleshooting → Re-run Wizard"</em>.</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img class="mx-auto" :src="require('@static/img/plugin_rerun_setup.png')">
              </div>
            </div>
          </div>
        </tab-content>
        <tab-content v-else title="Install Plugin">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>Open OctoPrint in another browser tab. </li>
                  <li>Select <em>"OctoPrint settings menu → Plugin Manager → Get More..."</em>.</li>
                  <li>Enter "The Spaghetti Detective" to locate the plugin. Click <em>"Install"</em>.</li>
                  <li>Restart OctoPrint when prompted.</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img
                  class="mx-auto screenshot"
                  :src="require('@static/img/install_plugin.png')"
                  @click="zoomIn($event)">
              </div>
            </div>
          </div>
        </tab-content>
        <tab-content title="Plugin Wizard">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>Wait for <em>"Access Anywhere - The Spaghetti Detective"</em> wizard to popup.</li>
                  <li>Follow the instructions in the wizard.</li>
                  <li>Select <em>"Web Setup"</em> when asked.</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img
                  class="mx-auto screenshot"
                  :src="require('@static/img/plugin_wizard_websetup.png')"
                  @click="zoomIn($event)">
              </div>
            </div>
          </div>
        </tab-content>
        <tab-content title="Enter Code">
          <div class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8  d-flex flex-column align-items-center">
                  <input disabled ref="code" class="code-btn" :value="`${verificationCode && verificationCode.code}`"/>
                  <small class="mx-auto py-1" :class="{'text-muted': !copied}">{{ copied ? 'Code copied to system clipboard' : 'Ctrl-C/Cmd-C to copy the code'}}</small>
                  <div class="mx-auto pt-1 pb-4"><span class="text-muted">Code expires in </span>{{timeToExpire}}</div>
                <div class="lead">Enter the <strong>6-digit verification code</strong> in the plugin</div>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img
                  class="screenshot"
                  :src="require('@static/img/plugin_verification_code.png')"
                  @click="zoomIn($event)">
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
        <div class="helper col-sm-12">Need help? Check out the <a href="https://help.thespaghettidetective.com/kb/guide/en/setup-the-spaghetti-detective-using-the-web-app-dbCcgiR0Tr/">step-by-step set up guide.</a></div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@lib/server_urls'
import {WizardButton, FormWizard, TabContent} from 'vue-form-wizard'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
import theme from '../main/main.sass'
import PullToReveal from '@common/PullToReveal.vue'
import Navbar from '@common/Navbar.vue'
import SavingAnimation from '../common/SavingAnimation.vue'

export default {
  components: {
    FormWizard,
    TabContent,
    WizardButton,
    PullToReveal,
    Navbar,
    SavingAnimation,
  },
  data() {
    return {
      theme: theme,
      verificationCode: null,
      verifiedPrinter: null,
      onVerificationStep: false,
      copied: false,
      saving: {},
      errorMessages: {},
      delayedSubmit: { // Make pause before sending new value to API
        'printer_name': {
          'delay': 1000,
          'timeoutId': null
        },
      }
    }
  },

  computed: {
    printerIdToLink() {
      return new URLSearchParams(window.location.search.substring(1)).get('printerId')
    },
    title() {
      return this.printerIdToLink ? 'Re-Link OctoPrint' : 'Link OctoPrint'
    },
    editPrinterUrl() {
      return `/printers/${this.verifiedPrinter.id}/`
    },
    expiryMoment() {
      if (this.verificationCode) {
        return moment(this.verificationCode.expired_at)
      } else {
        return null
      }
    },
    timeToExpire() {
      if (this.expiryMoment) {
        return moment.duration(this.expiryMoment.diff(moment())).humanize()
      } else {
        return '-'
      }
    }
  },
  methods: {
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },

    updatePrinterName() {
      if ('name' in this.verifiedPrinter && this.verifiedPrinter.name) {
        const delayInfo = this.delayedSubmit['printer_name']
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }

        this.delayedSubmit['printer_name']['timeoutId'] = setTimeout(() => {
          this.setSavingStatus('printer_name', true)

          // Make request to API
          return axios
            .patch(urls.printer(this.verifiedPrinter.id), {
              'name': this.verifiedPrinter.name
            })
            .catch(err => {
              console.log(err)
            })
            .then(() => {
              this.setSavingStatus('printer_name', false)
            })

        }, delayInfo['delay'])
        return
      } else {
        const delayInfo = this.delayedSubmit['printer_name']
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }
      }
    },

    /**
     * Functions prevTab() and nextTab() are used to remove .checked class from circle steps
     * following current step (.checked class isn't removed by default after clicking Back
     * button, which causes showiing logo inside furter steps, not only completed ones).
     */
    prevTab() {
      document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').classList.remove('checked')
      this.onVerificationStep = document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').id === 'step-PluginWizard1'
    },
    nextTab() {
      document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').classList.add('checked')

      this.onVerificationStep = document.querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle').id === 'step-PluginWizard1'

      if (this.onVerificationStep) {
        if (!this.codeInterval) {
          this.getVerificationCode()

          this.codeInterval = setInterval(() => {
            this.getVerificationCode()
          }, 5000)
        }

        const copyFunc = this.copyCode

        let ctrlDown = false, ctrlKey = 17, cmdKey = 91, cKey = 67

        document.addEventListener('keydown', function(e) {
          if (e.keyCode == ctrlKey || e.keyCode == cmdKey) ctrlDown = true
        })
        document.addEventListener('keyup', function(e) {
          if (e.keyCode == ctrlKey || e.keyCode == cmdKey) ctrlDown = false
        })

        document.addEventListener('keydown', function(e) {
          if (ctrlDown && (e.keyCode == cKey)) {
            copyFunc()
          }
        })
      }
    },
    verificationCodeUrl() {
      const baseUrl = urls.verificationCode()
      if (!this.verificationCode){ // Never retrieved veification code. Get one.
        if (this.printerIdToLink) {
          return `${baseUrl}?printer_id=${this.printerIdToLink}`
        } else {
          return baseUrl
        }
      }

      if (this.verificationCode.verified_at) { // Code is verified successfully, keep on polling to get update on the printer name if any
        return `${baseUrl}${this.verificationCode.id}/`
      }

      if (moment().isBefore(this.expiryMoment)) { // Not verified, and not expired
        return `${baseUrl}${this.verificationCode.id}/`
      }

      // Not verified, but expired.
      return baseUrl
    },
    /**
     * Copy verification code to clipboard (on appropriate step)
     */
    copyCode() {
      if (this.onVerificationStep) {
        let textArea = document.createElement('textarea')
        textArea.value = this.verificationCode.code

        // Avoid scrolling to bottom
        textArea.style.top = '0'
        textArea.style.left = '0'
        textArea.style.position = 'fixed'

        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()

        try {
          document.execCommand('copy')
          this.copied = true
        } catch (err) {
          console.error('Fallback: Oops, unable to copy', err)
        }

        document.body.removeChild(textArea)
      }
    },

    /**
     * Get verification code from API
     */
    getVerificationCode() {
      axios
        .get(this.verificationCodeUrl())
        .then((resp) => {
          if (resp.data) {
            if (resp.data) {
              this.verificationCode = resp.data
              if (this.verificationCode.verified_at) {
                this.verifiedPrinter = resp.data.printer
                clearInterval(this.codeInterval)
              }
            }
          }
        })
    },

    showVerificationCodeHelpModal() {
      this.$swal.fire({
        title: 'Can\'t find the page to enter the 6-digit code?',
        html: `<p>The 6-digit code needs to be entered in The Spaghetti Detective plugin in OctoPrint. There are a few reasons why you can't find this page:</p>
        <p><ul>
        <li style="margin: 10px 0;">You don't have the plugin installed or you haven't restarted OctoPrint after installation. Click <a href="/printers/wizard/">here</a> to walk through the process again.</li>
        <li style="margin: 10px 0;">The installed plugin is on a version earlier than 1.5.0. You need to upgrade the plugin to <b>1.5.0</b> or later.</li>
        <li style="margin: 10px 0;">Still no dice? Check out the step-by-step <a href="https://help.thespaghettidetective.com/kb/guide/en/setup-the-spaghetti-detective-using-the-web-app-dbCcgiR0Tr/">set up guide</a>.</li>
        </ul></p>`,
        customClass: {
          container: 'dark-backdrop',
        },
      })
    },

    zoomIn(event) {
      event.target.classList.toggle('zoomedIn')
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.wizard-btn
  border-radius: 300px

.wizard-container
  padding: 1em
  background: rgb(var(--color-body-bg))
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important

  &.logo-bg
    background-image: var(--url-logo-bg)
    background-repeat: no-repeat
    background-position: -250px 100px
    background-size: 500px

.btn-back
  color: rgb(var(--color-white))
  min-width: auto

.container
  padding: 0

.header-img
  width: 1em
  height: 1em
  margin-right: 12px
  margin-bottom: 8px

  .tone-1
    fill: rgb(var(--color-icon-tunneling-tone-1))
    
  .tone-2
    fill: rgb(var(--color-icon-tunneling-tone-2))

.img-container
  background: rgb(var(--color-body-bg-d-5))
  padding: 1rem
  text-align: center

img
  max-height: 30vh

.spacer
 width: 200px

.code-btn
  border-radius: 10px
  text-align: center
  width: 21rem
  height: 60px
  background-color: rgb(var(--color-body-bg-d-10))
  color: rgb(var(--color-text))
  font-size: 2rem
  font-weight: 500
  letter-spacing: 0.5em
  border: none

.helper
  text-align: center
  padding: 0 36px

li
  margin: 2px -35px

.screenshot
  max-width: 100%
  transition: transform .3s

  &:hover
    cursor: pointer

  &.zoomedIn
    transform: scale(2)
    position: relative
    z-index: 9
</style>

<style lang="sass">
// Unscoped styles to style plugin elements
@use "~main/theme"

// Step label (not active)
.wizard-container .vue-form-wizard .wizard-nav-pills > li:not(.active) > a > span
  color: rgb(var(--color-white))

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
    background-image: var(--url-logo-bg)
    background-size: $size $size
    position: absolute
    top: calc(50% - #{$size / 2})
    left: calc(50% - #{$size / 2})
    bottom: calc(50% - #{$size / 2})
    right: calc(50% - #{$size / 2})

.success-checkmark
  height: 6rem
  margin-bottom: 1.5rem

  path
    fill: rgb(var(--color-dark-white))

.printer-name-input
  position: relative

  .edit-icon
    height: 100%
    display: flex
    flex-direction: column
    justify-content: center
    position: absolute
    top: 0
    left: 1em
    opacity: .5

  input
    padding: .4em 2.4em
    width: 100%
    font-size: 20px
    text-align: center
</style>
