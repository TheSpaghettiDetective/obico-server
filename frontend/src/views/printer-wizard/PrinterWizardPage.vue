<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row>
          <b-col>
            <div class="wizard-container form-container full-on-mobile">
              <div v-if="verifiedPrinter" class="text-center py-5">
                <svg class="success-checkmark">
                  <use href="#svg-success-checkmark" />
                </svg>
                <h3 class="pb-4">Successfully linked to your account!</h3>
                <div
                  class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center"
                >
                  <saving-animation
                    :errors="errorMessages.printer_name"
                    :saving="saving.printer_name"
                  >
                    <div class="printer-name-input">
                      <div class="edit-icon">
                        <i class="fas fa-pen"></i>
                      </div>
                      <input
                        v-model="verifiedPrinter.name"
                        type="text"
                        class="dark"
                        placeholder="Printer name"
                        @input="updatePrinterName"
                      />
                    </div>
                  </saving-animation>
                  <div>
                    <div class="text-muted mx-auto text-center font-weight-light">
                      Give your printer a shiny name.
                    </div>
                  </div>
                </div>
                <br /><br />
                <div
                  class="col-sm-12 col-md-8 offset-md-2 col-lg-6 offset-lg-3 d-flex flex-column align-center justify-content-center"
                >
                  <div v-if="redirectToTunnelCreation" class="mt-4">
                    <a
                      :href="redirectToTunnelCreation"
                      class="btn btn-primary btn-block mx-auto btn-lg"
                      >Authorize App Access</a
                    >
                  </div>
                  <div v-else>
                    <div class="mt-4">
                      <a href="/printers/" class="btn btn-primary btn-block mx-auto btn-lg"
                        >Go Check Out Printer Feed!</a
                      >
                    </div>
                    <div class="mt-5">
                      <a
                        href="/user_preferences/notification_twilio/"
                        class="btn btn-outline-secondary btn-block mx-auto"
                        >Add Phone Number</a
                      >
                    </div>
                    <div>
                      <div class="text-muted mx-auto text-center font-weight-light">
                        Receive text (SMS) in case of print failures.
                      </div>
                    </div>
                    <div class="mt-4">
                      <a :href="editPrinterUrl" class="btn btn-outline-secondary btn-block mx-auto"
                        >Change Printer Settings</a
                      >
                    </div>
                    <div>
                      <div class="text-muted mx-auto text-center font-weight-light">
                        You can always change it later.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else>
                <div v-if="$route.path === routes.printerWizardSetup">
                  <form-wizard color="var(--color-primary)" step-size="sm">
                    <h3 slot="title">
                      {{ title }}
                    </h3>

                    <tab-content v-if="targetMoonraker" :title="`Install ${$t('name')} for Klipper`">
                      <div class="container">
                        <div class="row justify-content-center pb-3">
                          <div class="col-sm-12 col-lg-8">
                            <ol>
                              <li>SSH to the Raspberry Pi your Klipper runs on.</li>
                              <li>
                                <div>Run:</div>
                                <pre class="mt-2">
cd ~
git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
cd moonraker-obico
./install.sh
                              </pre
                                >
                              </li>
                              <li>Follow the installation steps.</li>
                            </ol>
                          </div>
                        </div>
                      </div>
                    </tab-content>
                    <tab-content
                      v-if="printerIdToLink && targetOctoPrint"
                      title="Open Plugin Settings"
                    >
                      <div class="container">
                        <div class="row justify-content-center pb-3">
                          <div class="col-sm-12 col-lg-8">
                            <div class="text-warning">
                              Warning: Re-Linking OctoPrint should be your last resort to solve
                              issues. Please make sure you have exhausted all options on
                              <a href="https://www.obico.io/help/">{{ $t('brand_name') }}'s help website</a>.
                            </div>
                            <ol>
                              <li>Open OctoPrint in another browser tab.</li>
                              <li>
                                Select <em>"OctoPrint settings menu → {{ $t('brand_name') }} for OctoPrint"</em>.
                              </li>
                              <li>Select <em>"Troubleshooting → Re-run Wizard"</em>.</li>
                            </ol>
                          </div>
                        </div>
                        <div class="row justify-content-center">
                          <div class="col-sm-12 col-lg-8 img-container">
                            <img
                              class="mx-auto"
                              :src="
                                require('@static/img/octoprint-plugin-guide/plugin_rerun_setup.png')
                              "
                            />
                          </div>
                        </div>
                      </div>
                    </tab-content>
                    <tab-content v-if="!printerIdToLink && targetOctoPrint" title="Install Plugin">
                      <div class="container">
                        <div class="row justify-content-center pb-3">
                          <div class="col-sm-12 col-lg-8">
                            <ol>
                              <li>Open OctoPrint in another browser tab.</li>
                              <li>
                                Select
                                <em>"OctoPrint settings menu → Plugin Manager → Get More..."</em>.
                              </li>
                              <li>Enter "{{ $t('brand_name') }}" to locate the plugin. Click <em>"Install"</em>.</li>
                              <li>Restart OctoPrint when prompted.</li>
                            </ol>
                          </div>
                        </div>
                        <div class="row justify-content-center">
                          <div class="col-sm-12 col-lg-8 img-container">
                            <img
                              class="mx-auto screenshot"
                              :src="
                                require('@static/img/octoprint-plugin-guide/install_plugin.png')
                              "
                              @click="zoomIn($event)"
                            />
                          </div>
                        </div>
                      </div>
                    </tab-content>
                    <template v-if="discoveryEnabled">
                      <tab-content title="Link It!">
                        <loading :active="chosenDeviceId != null" :can-cancel="false"> </loading>
                        <div class="discover">
                          <div class="discover-body">
                            <div v-if="!canStartLinking" style="text-align: center">
                              <div class="spinner-border big" role="status">
                                <span class="sr-only"></span>
                              </div>
                              <div class="lead">Scanning...</div>
                            </div>
                            <div v-else>
                              <div class="lead my-3">
                                <div class="spinner-border" role="status">
                                  <span class="sr-only"></span>
                                </div>
                                <span class="sr-only"></span>Scanning...,
                                {{ discoveredPrinters.length }} printer(s) found on your local
                                network:
                              </div>
                              <discovered-printer
                                v-for="discoveredPrinter in discoveredPrinters"
                                :key="discoveredPrinter.device_id"
                                :discovered-printer="discoveredPrinter"
                                @auto-link-printer="autoLinkPrinter"
                              />
                            </div>
                            <div class="mt-5 mb-3">
                              Can't find the printer you want to link? Switch to
                              <a class="link" @click="discoveryEnabled = false">Manual Setup</a>
                              instead.
                            </div>
                            <div v-if="discoveryCount >= 2" class="text-muted">
                              <div>To link your printer, please make sure:</div>
                              <ul>
                                <li>The printer is powered on. If you are using an external SBC such as a Raspberry Pi, make sure it's powered on as well.</li>
                                <li>
                                  The printer or SBC is connected to the same local network as your
                                  phone/computer.
                                </li>
                                <li v-if="targetOctoPrint">{{ $t('brand_name') }} for OctoPrint is 1.8.0 or above.</li>
                                <li v-else>{{ $t('brand_name') }} for Klipper is 1.5.0 or above.</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </tab-content>
                    </template>
                    <template v-else>
                      <tab-content v-if="targetOctoPrint" title="Plugin Wizard">
                        <div class="container">
                          <div class="row justify-content-center pb-3">
                            <div class="col-sm-12 col-lg-8">
                              <ol>
                                <li>Wait for <em>"{{ $t('brand_name') }} for OctoPrint"</em> wizard to popup.</li>
                                <li>Follow the instructions in the wizard.</li>
                                <li>Select <em>"Web Setup"</em> when asked.</li>
                              </ol>
                            </div>
                          </div>
                          <div class="row justify-content-center">
                            <div class="col-sm-12 col-lg-8 img-container">
                              <img
                                class="mx-auto screenshot"
                                :src="
                                  require('@static/img/octoprint-plugin-guide/plugin_wizard_websetup.png')
                                "
                                @click="zoomIn($event)"
                              />
                            </div>
                          </div>
                        </div>
                      </tab-content>
                      <tab-content title="Enter Code">
                        <div class="container">
                          <div class="row justify-content-center pb-3">
                            <div class="col-sm-12 col-lg-8 d-flex flex-column align-items-center">
                              <input
                                ref="code"
                                disabled
                                class="code-btn"
                                :value="`${verificationCode && verificationCode.code}`"
                              />
                              <small class="mx-auto py-1" :class="{ 'text-muted': !copied }">{{
                                copied
                                  ? 'Code copied to system clipboard'
                                  : 'Ctrl-C/Cmd-C to copy the code'
                              }}</small>
                              <div class="mx-auto pt-1 pb-4">
                                <span class="text-muted">Code will expire in </span
                                >{{ timeToExpire }}
                              </div>
                              <div class="lead">
                                Enter the <strong>6-digit verification code</strong>
                              </div>
                            </div>
                          </div>
                          <div class="row justify-content-center">
                            <div class="col-sm-12 col-lg-8 img-container">
                              <img
                                v-if="targetOctoPrint"
                                class="screenshot"
                                :src="
                                  require('@static/img/octoprint-plugin-guide/plugin_verification_code.png')
                                "
                                @click="zoomIn($event)"
                              />
                              <img
                                v-if="targetMoonraker"
                                class="screenshot"
                                :src="
                                  require('@static/img/octoprint-plugin-guide/moonraker_verification_code.png')
                                "
                                @click="zoomIn($event)"
                              />
                              <div class="helper mx-auto py-2">
                                <a
                                  class="link font-weight-bold"
                                  @click="showVerificationCodeHelpModal"
                                  >Can't find the page to enter the 6-digit code?</a
                                >
                              </div>
                            </div>
                          </div>
                        </div>
                      </tab-content>
                    </template>

                    <template slot="footer" slot-scope="props">
                      <div class="wizard-footer-left">
                        <wizard-button
                          v-if="props.activeTabIndex > 0"
                          class="btn btn-link btn-back"
                          @click.native="
                            props.prevTab()
                            prevTab(props.activeTabIndex)
                          "
                          >&lt; Back</wizard-button
                        >
                      </div>
                      <div class="wizard-footer-right">
                        <wizard-button
                          v-if="!props.isLastStep"
                          class="wizard-footer-right wizard-btn"
                          :style="{ ...props.fillButtonStyle, color: 'var(--color-on-primary)' }"
                          @click.native="
                            props.nextTab()
                            nextTab(props.activeTabIndex)
                          "
                          >Next &gt;</wizard-button
                        >
                      </div>
                    </template>
                  </form-wizard>
                  <div class="row">
                    <div class="helper col-sm-12">
                      Need help? Check out the
                      <a
                        target="_blank"
                        :href="
                          targetMoonraker
                            ? 'https://www.obico.io/docs/user-guides/klipper-setup/'
                            : 'https://www.obico.io/docs/user-guides/octoprint-plugin-setup/'
                        "
                        >step-by-step set up guide.</a
                      >
                    </div>
                  </div>
                </div>
                <div v-else class="container">
                  <div class="row">
                    <h3 class="col-sm-12 text-center p-3">Which platform are you using?</h3>
                  </div>
                  <div class="row">
                    <div class="col-sm-12 col-lg-6 p-4">
                      <div class="wizard-card" @click="setTargetPlatform('octoprint')">
                        <img :src="require('@static/img/octoprint_logo.png')" />
                        <h3 class="mt-4">OctoPrint</h3>
                        <div>Including OctoPrint for Klipper such as OctoKlipper.</div>
                      </div>
                    </div>
                    <div class="col-sm-12 col-lg-6 p-4">
                      <div class="wizard-card" @click="setTargetPlatform('moonraker')">
                        <div>
                          <img :src="require('@static/img/klipper_logo.jpg')" />
                          <img :src="require('@static/img/mainsail_logo.png')" />
                          <img :src="require('@static/img/fluidd_logo.png')" />
                        </div>
                        <h3 class="mt-4">Klipper</h3>
                        <h5>with Mainsail/Fluidd/Moonraker</h5>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@config/server-urls'
import { onPrinterLinked } from '@config/event-handler'
import routes from '@src/views/printer-wizard/wizard-routes'
import { WizardButton, FormWizard, TabContent } from 'vue-form-wizard'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'
import sortBy from 'lodash/sortBy'
import theme from '@src/styles/main.sass'
import PageLayout from '@src/components/PageLayout.vue'
import SavingAnimation from '@src/components/SavingAnimation.vue'
import DiscoveredPrinter from '@src/components/printers/DiscoveredPrinter.vue'
import AutoLinkPopup from '@src/components/printers/AutoLinkPopup.vue'
const MAX_DISCOVERY_CALLS = 60 // Scaning for up to 5 minutes

export default {
  components: {
    FormWizard,
    TabContent,
    WizardButton,
    Loading,
    PageLayout,
    SavingAnimation,
    DiscoveredPrinter,
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
      delayedSubmit: {
        // Make pause before sending new value to API
        printer_name: {
          delay: 1000,
          timeoutId: null,
        },
      },
      discoveryEnabled: true, // To simplify the flow, this can only change from true -> false.
      discoveryCount: 0,
      discoveredPrinters: [],
      chosenDeviceId: null,
      gotSecret: null,
      obicoDiscoveryPopup: null,
      apiCallIntervalId: null,
      targetPlatform: null,
      routes,
    }
  },
  computed: {
    printerIdToLink() {
      return new URLSearchParams(window.location.search.substring(1)).get('printerId')
    },
    title() {
      return this.printerIdToLink ? 'Re-Link Printer' : 'Link Printer'
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
    },
    canStartLinking() {
      return this.verificationCode?.code && this.discoveredPrinters?.length > 0
    },
    redirectToTunnelCreation() {
      return new URLSearchParams(window.location.search).get('redirectToTunnelCreation')
    },
    targetOctoPrint() {
      return this.targetPlatform === 'octoprint'
    },
    targetMoonraker() {
      return this.targetPlatform === 'moonraker'
    },
  },
  created() {
    if (this.printerIdToLink) {
      // Re-link currently doesn't support auto-discovery on the plugin side
      this.discoveryEnabled = false
    }
    this.getVerificationCode()

    // Start from platform selection after page refresh
    if (this.$route.path !== routes.printerWizard) {
      this.$router.push(routes.printerWizard + `?${window.location.search}`)
    }
  },
  methods: {
    setTargetPlatform(platfrom) {
      this.targetPlatform = platfrom
      this.$router.push(routes.printerWizardSetup + `?${window.location.search}`)
    },
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
              name: this.verifiedPrinter.name,
            })
            .then(() => {
              this.setSavingStatus('printer_name', false)
            })
            .catch((error) => {
              this.errorDialog(error, 'Failed to update printer name')
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
      document
        .querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle')
        .classList.remove('checked')
      this.onVerificationStep = false
    },
    nextTab(activeStep) {
      document
        .querySelector('.wizard-nav.wizard-nav-pills li.active .wizard-icon-circle')
        .classList.add('checked')
      this.onVerificationStep = activeStep == 1 // nextTab is called before activeStep changes
      if (activeStep == 0 && this.discoveryEnabled && this.discoveryCount == 0) {
        this.discoverPrinter()
      }
      if (this.onVerificationStep) {
        const copyFunc = this.copyCode
        let ctrlDown = false,
          ctrlKey = 17,
          cmdKey = 91,
          cKey = 67
        document.addEventListener('keydown', function (e) {
          if (e.keyCode == ctrlKey || e.keyCode == cmdKey) ctrlDown = true
        })
        document.addEventListener('keyup', function (e) {
          if (e.keyCode == ctrlKey || e.keyCode == cmdKey) ctrlDown = false
        })
        document.addEventListener('keydown', function (e) {
          if (ctrlDown && e.keyCode == cKey) {
            copyFunc()
          }
        })
      }
    },
    verificationCodeUrl() {
      const baseUrl = urls.verificationCode()
      if (!this.verificationCode) {
        // Never retrieved veification code. Get one.
        if (this.printerIdToLink) {
          return `${baseUrl}?printer_id=${this.printerIdToLink}`
        } else {
          return baseUrl
        }
      }
      if (this.verificationCode.verified_at) {
        // Code is verified successfully, keep on polling to get update on the printer name if any
        return `${baseUrl}${this.verificationCode.id}/`
      }
      if (moment().isBefore(this.expiryMoment)) {
        // Not verified, and not expired
        return `${baseUrl}${this.verificationCode.id}/`
      }
      // Not verified, but expired.
      return baseUrl
    },
    /**
     * Copy verification code to clipboard (on appropriate step)
     */
    copyCode() {
      if (this.onVerificationStep && this.verificationCode) {
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
    callVerificationCodeApi() {
      axios.get(this.verificationCodeUrl()).then((resp) => {
        if (resp.data) {
          this.verificationCode = resp.data
          if (this.verificationCode.verified_at) {
            this.verifiedPrinter = resp.data.printer
            if (onPrinterLinked) {
              onPrinterLinked()
            }
          }
        }
      })
    },
    getVerificationCode() {
      this.callVerificationCodeApi()
      this.apiCallIntervalId = setInterval(() => {
        if (this.verifiedPrinter) {
          clearInterval(this.apiCallIntervalId)
        } else {
          this.callVerificationCodeApi()
        }
      }, 5000)
    },
    showVerificationCodeHelpModal() {
      let html = `<p>The 6-digit code needs to be entered in the ${ this.$t('name') } plugin in OctoPrint. There are a few reasons why you can't find this page:</p>
        <p><ul>
        <li style="margin: 10px 0;">You don't have the plugin installed or you haven't restarted OctoPrint after installation. Click <a href="/printers/wizard/">here</a> to walk through the process again.</li>
        <li style="margin: 10px 0;">The installed plugin is on a version earlier than 1.5.0. You need to upgrade the plugin to <b>1.5.0</b> or later.</li>
        <li style="margin: 10px 0;">Still no dice? Check out the step-by-step <a target="_blank" href="https://www.obico.io/docs/user-guides/octoprint-plugin-setup/">set up guide</a>.</li>
        </ul></p>`

      if (!this.targetOctoPrint) {
        html = `<p>The 6-digit code needs to be entered to the <em>${ this.$t('name') } for OctoPrint</em> installation script.</p>
        <p>Check <a target="_blank" href="https://www.obico.io/docs/user-guides/klipper-setup/">this set up guide</a> for detailed instructions.</p>`
      }

      this.$swal.fire({
        title: "Can't find the page to enter the 6-digit code?",
        html,
        customClass: {
          container: 'dark-backdrop',
        },
      })
    },
    zoomIn(event) {
      event.target.classList.toggle('zoomedIn')
    },
    callPrinterDiscoveryApi() {
      if (!this.discoveryEnabled) {
        return
      }
      if (this.discoveryCount >= MAX_DISCOVERY_CALLS && this.discoveredPrinters.length === 0) {
        this.discoveryEnabled = false
        this.$swal.Toast.fire({
          title: 'No OctoPrint discovered on your local network. Switched to manual linking.',
        })
      }
      this.discoveryCount += 1
      axios.get(urls.printerDiscovery()).then((resp) => {
        this.discoveredPrinters = sortBy(resp.data, (p) => p.device_id)
      })
    },
    discoverPrinter() {
      if (!this.discoveryEnabled || this.verifiedPrinter) {
        return
      }
      this.callPrinterDiscoveryApi()
      setTimeout(() => {
        this.discoverPrinter()
      }, 5000)
    },
    autoLinkPrinter(discoveredPrinter) {
      this.$swal.openModalWithComponent(
        AutoLinkPopup,
        {
          discoveredPrinter,
          switchToManualLinking: () => (this.discoveryEnabled = false),
          secretObtained: (chosenDeviceId, secret) => this.secretObtained(chosenDeviceId, secret),
        },
        {
          title: 'Browser Pop-up',
          showConfirmButton: false,
          allowOutsideClick: false,
        }
      )
    },
    secretObtained(chosenDeviceId, secret) {
      this.chosenDeviceId = chosenDeviceId
      axios.post(urls.printerDiscovery(), {
        code: this.verificationCode.code,
        device_id: this.chosenDeviceId,
        device_secret: secret,
      })
      // Declare failure if nothing is linked after 20s
      setTimeout(() => {
        if (this.chosenDeviceId && !this.verifiedPrinter) {
          this.chosenDeviceId = null
          this.$swal.Toast.fire({
            icon: 'error',
            title: 'Something went wrong. Switched to using 6-digit code to link OctoPrint.',
          })
          this.discoveryEnabled = false
        }
        this.chosenDeviceId = null
      }, 20000)
    },
  },
}
</script>

<style lang="sass" scoped>

.wizard-card
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-lg)
  padding: 1em
  display: flex
  flex-direction: column
  align-items: center
  min-height: 24em
  justify-content: center
  text-align: center
  &:hover
    cursor: pointer
    color: var(--color-primary)
    background-color: var(--color-hover)
.wizard-card img
  height: 3em
  margin: 1em

.wizard-btn
  border-radius: 300px
.wizard-container
  padding: 1em
  background: var(--color-surface-secondary)
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important
  border-radius: var(--border-radius-lg)
.btn-back
  color: var(--color-text-primary)
  min-width: auto
.header-img
  width: 1em
  height: 1em
  margin-right: 12px
  margin-bottom: 8px
.img-container
  padding: 1rem
  text-align: center
img
  max-height: 30vh
.spacer
 width: 200px
.code-btn
  border-radius: var(--border-radius-sm)
  text-align: center
  width: 21rem
  height: 60px
  background-color: var(--color-input-background)
  color: var(--color-text-primary)
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

pre
  color: var(--color-text-secondary)
  font-size: 0.9em
</style>

<style lang="sass">
// Unscoped styles to style plugin elements
// TODO merge 2 style blocks

// Step label (not active)
.wizard-container .vue-form-wizard .wizard-nav-pills > li:not(.active) > a > span
  color: var(--color-text-primary)
// Adjust numbers in the circles (form steps)
.wizard-nav.wizard-nav-pills .wizard-icon-circle i
  position: relative
  right: 2px
// Show logo inside completed sorm step circles
.wizard-nav.wizard-nav-pills li:not(.active)
  .wizard-icon-circle.checked i
    display: none
  .wizard-icon-circle.checked
    background-color: var(--color-primary)
    &:before
      $size: 20px
      content: ""
      display: block
      width: $size
      height: $size
      background-image: url('/static/img/tick_dark.svg')
      background-size: $size $size
      position: absolute
      top: calc(50% - $size / 2)
      left: calc(50% - $size / 2)
      bottom: calc(50% - $size / 2)
      right: calc(50% - $size / 2)
.success-checkmark
  width: 6rem
  height: 6rem
  margin-bottom: 1.5rem
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
.discover
  .discover-body
    min-height: 25rem
    display: flex
    flex-direction: column
    justify-content: center
    .spinner-border
      width: 1.2em
      height: 1.2em
      margin-right: 0.2em
      &.big
        width: 5rem
        height: 5rem
        margin-bottom: 0.8rem
  li
    margin: initial
</style>
