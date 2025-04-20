<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row>
          <b-col>
            <div class="form-container full-on-mobile border-radius-lg">
              <div class="row">
                <h3 class="col-sm-12 text-center p-3 wizard-page-title-font">{{ $t("Link Printer") }}</h3>
              </div>
              <b-row class="center mt-3 mb-5">
                <div class="col-sm-12 col-lg-8">
                  <PrinterProgress :step="2"></PrinterProgress>
                </div>
              </b-row>

              <b-row class="center py-5">
                <div class="col-sm-12 col-lg-8">
                  <loading :active="chosenDeviceId != null" :can-cancel="false"> </loading>
                  <div v-if="discoveryEnabled" class="discover">
                    <div class="discover-body">
                      <div v-if="!canStartLinking" style="text-align: center">
                        <div class="spinner-border big" role="status">
                          <span class="sr-only"></span>
                        </div>
                        <div class="lead">{{ $t("Scanning...") }}</div>
                      </div>
                      <div v-else>
                        <div class="lead my-3">
                          <div class="spinner-border" role="status">
                            <span class="sr-only"></span>
                          </div>
                          <span class="sr-only"></span>
                          {{ $t("Scanning..., {name} printer(s) found on your local network:",{name:discoveredPrinters.length}) }}
                        </div>
                        <discovered-printer
                          v-for="discoveredPrinter in discoveredPrinters"
                          :key="discoveredPrinter.device_id"
                          :discovered-printer="discoveredPrinter"
                          @auto-link-printer="autoLinkPrinter"
                        />
                      </div>
                      <div v-if="discoveryCount >= 2" class="text-muted pt-4">
                        <div>{{$t("To link your printer, please make sure:")}}</div>
                        <ul>
                          <li>{{ $t("The printer is powered on. If you are using an external SBC such as a Raspberry Pi, make sure it's powered on as well.") }}</li>
                          <li>
                            {{$t("The printer or SBC is connected to the same local network as your phone/computer.")}}
                          </li>
                          <li v-if="targetOctoPrint">{{ $t("{brandName} for OctoPrint is 1.8.0 or above.",{brandName:$syndicateText.brandName}) }}</li>
                        </ul>
                      </div>
                      <div class="d-flex flex-column align-items-center">
                        <div class="mt-5 mb-3">
                        {{ $t(`Can’t find the printer you want to link? Switch to Manual Linking instead.`) }}
                        </div>
                        <button
                          class="btn btn-outline-secondary"
                          type="button"
                          @click="discoveryEnabled = false"
                        >
                          {{ $t("Switch to Manual Linking") }}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="useLegacyVerificationCode" class="container">
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
                            ? $t('Code copied to system clipboard')
                            : $t('Ctrl-C/Cmd-C to copy the code')
                        }}</small>
                        <div class="mx-auto pt-1 pb-4">
                          <span class="text-muted">{{ $t("Code will expire in ") }}</span
                          >{{ timeToExpire }}
                        </div>
                        <div class="lead">
                          <i18next :translation="$t(`Enter the {localizedDom}`)">
                            <template #localizedDom>
                              <strong>{{$t("6-digit verification code")}}</strong>
                            </template>
                          </i18next>
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
                          v-if="targetKlipper"
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
                            >{{ $t("Can't find the page to enter the 6-digit code?") }}</a
                          >
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="container pt-5">
                    <div class="row justify-content-center pb-1">
                      <div class="col-sm-12 col-md-8 col-lg-6 d-flex flex-column align-items-center">
                        <div class="d-flex align-items-center">
                          <input
                            type="text"
                            class="form-control code-btn"
                            aria-label="One-time Passcode"
                            v-model="oneTimePasscode"
                            :disabled="oneTimePasscodeStatus === 'inprogress'"
                            @input="oneTimePasscodeChanged"
                          />
                          <div class="spinner-border text-primary ml-2" role="status" v-if="oneTimePasscodeStatus === 'inprogress'">
                            <span class="sr-only">Loading...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="row justify-content-center pb-3">
                      <div v-if="oneTimePasscodeStatus === 'failed'" class="text-danger col-sm-12 d-flex flex-column align-items-center wizard-secondary-text-font text-secondary">
                        {{$t("Invalid code. Is it expired?")}}
                      </div>
                      <div v-else class="col-sm-12 d-flex flex-column align-items-center wizard-secondary-text-font text-secondary">
                        {{$t("Enter the One-time Passcode")}}
                      </div>
                    </div>
                    <div class="mt-4">
                      <muted-alert class="muted-alert wizard-secondary-text-font text-secondary">
                        <i18next class="" :translation="$t(`If you using Obico for OctoPrint older than 2.5.0, or Obico for Klipper older than 1.6.0, switch to {localizedDom}.`)">
                          <template #localizedDom>
                            <a class="link" @click="useLegacyVerificationCode = true">{{$t("6-digit verification code")}}</a>
                          </template>
                        </i18next>
                      </muted-alert>
                    </div>
                  </div>
                </div>
              </b-row>
              <b-row v-if="!discoveryEnabled && !useLegacyVerificationCode" class="mt-3 mb-5">
                <div class="col-md-4 p-4 method-block">
                    <h4 class="text-center font-weight-bold wizard-page-title-font">{{ $t("Touch Screen") }}</h4>
                    <div class="image-block">
                      <img src="@static/img/printer-wizard/klipperScreenMenu.png" style="max-width: 80%;" alt="">
                    </div>
                    <ol>
                      <li>{{ $t("Check to see if your printer already has Obico installed your printer screen.") }}</li>
                      <li>{{ $t("Navigate to the settings menu on the LCD screen of your printer.") }}</li>
                      <li>{{ $t("Find the “Link Obico” menu item and tap it to open the connection screen.") }}</li>
                    </ol>
                </div>
                <div class="col-md-4 p-4 method-block">
                    <h4 class="text-center font-weight-bold wizard-page-title-font">{{ $t("LCD Screen ") }}</h4>
                    <div class="image-block">
                      <img src="@static/img/printer-wizard/lcdScreenLarge.png" style="max-width: 80%;" alt="">
                    </div>
                    <ol>
                      <li>{{ $t("Check to see if your printer already has Obico Easy Link installed on the LCD menu.") }}</li>
                      <li>{{ $t("Navigate to the settings menu on the LCD screen of your printer.") }}</li>
                      <li>{{ $t("Find the “Link Obico” menu item.") }}</li>
                    </ol>
                </div>
                <div class="col-md-4 p-4 method-block">
                    <h4 class="text-center font-weight-bold wizard-page-title-font">{{ $t("Install Via SSH") }}</h4>
                    <div class="image-block">
                      <img src="@static/img/printer-wizard/commandLinePrompt.png" style="max-width: 80%;" alt="">
                    </div>
                    <ol>
                      <li>{{ $t("If you can't find Obico Easy Link, you will need to SSH to your printer to install Obico. You will need to find a guide that works for your printer.") }}</li>
                    </ol>
                    <div>
                      <a target="_blank" :href="getDocUrl('/user-guides/klipper-setup/')">{{ $t("Show me how") }}</a>
                    </div>
                </div>
              </b-row>
              <div class="d-flex justify-content-between align-items-center button-wrap">
                <div class="back" @click="$router.back()">
                  <i class="fas fa-chevron-left"></i>
                  <span> {{ $t("Back") }}</span>
                </div>
              </div>
              <div class="text-center mt-5 wizard-default-font">
                <i18next :translation="$t(`Need help? Check out the {localizedDom}`)">
                  <template #localizedDom>
                    <a target="_blank" :href="targetKlipper? getDocUrl('/user-guides/klipper-setup/'):getDocUrl('/user-guides/octoprint-plugin-setup/')">{{$t("step-by-step set up guide")}}.</a>
                  </template>
                </i18next>
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
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'
import sortBy from 'lodash/sortBy'
import theme from '@src/styles/main.sass'
import PageLayout from '@src/components/PageLayout.vue'
import MutedAlert from '@src/components/MutedAlert.vue'
import DiscoveredPrinter from '@src/components/printers/wizard/DiscoveredPrinter.vue'
import AutoLinkPopup from '@src/components/printers/wizard/AutoLinkPopup.vue'
import PrinterProgress from '../../components/printers/wizard/PrinterProgress.vue';

export default {
  components: {
    Loading,
    PageLayout,
    DiscoveredPrinter,
    PrinterProgress,
    MutedAlert,
  },
  data() {
    return {
      theme: theme,
      verificationCode: null,
      verifiedPrinter: null,
      copied: false,
      oneTimePasscode: '',
      oneTimePasscodeStatus: null,
      useLegacyVerificationCode: false, // To simplify the flow, this can only change from false -> true.
      discoveryEnabled: true,
      discoveryCount: 0,
      discoveredPrinters: [],
      chosenDeviceId: null,
      gotSecret: null,
      obicoDiscoveryPopup: null,
      apiCallIntervalId: null,
    }
  },
  computed: {
    printerIdToLink() {
      return this.$route.query.printerId;
    },
    title() {
      return this.printerIdToLink ? 'Re-Link Printer' : 'Link Printer'
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
    targetOctoPrint() {
      return this.$route.params.targetPlatform === 'octoprint'
    },
    targetKlipper() {
      return this.$route.params.targetPlatform.startsWith('klipper-');
    },
  },
  created() {
    if (this.targetOctoPrint) {
      this.useLegacyVerificationCode = true
    }
    this.getVerificationCode()
    this.discoverPrinter()
  },
  methods: {
    oneTimePasscodeChanged() {
      this.oneTimePasscode = this.oneTimePasscode.toLowerCase();

      // Call API when input reaches 5 characters
      if (this.oneTimePasscode.length === 5) {
        this.oneTimePasscodeStatus = 'inprogress'
        axios
          .post(urls.oneTimePasscodes(), {
            one_time_passcode: this.oneTimePasscode,
            verification_code: this.verificationCode.code,
          })
          .then((resp) => {
            if (resp.status !== 200) {
              this.oneTimePasscodeStatus = 'failed'
            }
          })
          .catch((error) => {
            this.oneTimePasscodeStatus = 'failed'
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
    callVerificationCodeApi() {
      axios.get(this.verificationCodeUrl()).then((resp) => {
        if (resp.data) {
          this.verificationCode = resp.data
          if (this.verificationCode.verified_at) {
            this.verifiedPrinter = resp.data.printer
            if (onPrinterLinked) {
              onPrinterLinked()
            }
            this.$router.push({
              path: `/printers/wizard/success/${this.verifiedPrinter.id}/`,
              query: {
                ...this.$route.query,
              }
            })
            .catch((error) => {}) // There are NavigationDuplicated errors. Suspect it's because the setInterval is not super clean and occasionally results in multiple calls to this.
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
      let html = `<p>${this.$i18next.t("The 6-digit code needs to be entered in the Obico plugin in OctoPrint. There are a few reasons why you can't find this page:",{brandName:this.$syndicateText.brandName})}</p>
        <p><ul>
        <li style="margin: 10px 0;">${this.$i18next.t("You don't have the plugin installed or you haven't restarted OctoPrint after installation. Click")} <a href="/printers/wizard/">here</a> ${this.$i18next.t("to walk through the process again.")}</li>
        <li style="margin: 10px 0;">${this.$i18next.t("The installed plugin is on a version earlier than 1.5.0. You need to upgrade the plugin to")} <b>1.5.0</b> ${this.$i18next.t("or later.")}</li>
        <li style="margin: 10px 0;">${this.$i18next.t("Still no dice? Check out the step-by-step")} <a target="_blank" href=${this.getDocUrl('/user-guides/octoprint-plugin-setup/')}">${this.$i18next.t("set up guide")}</a>.</li>
        </ul></p>`

      if (!this.targetOctoPrint) {
        html = `<p>${this.$i18next.t("The 6-digit code needs to be entered to the Obico for Klipper installation script.")}</p>
        <p>${this.$i18next.t("Check")} <a target="_blank" href=${this.getDocUrl('/user-guides/klipper-setup/')}> ${this.$i18next.t("this set up guide")}</a> ${this.$i18next.t("for detailed instructions.")}</p>`
      }

      this.$swal.fire({
        title: `${this.$i18next.t("Can't find the page to enter the 6-digit code?")}`,
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
.method-block
  display: flex
  flex-direction: column
  align-items: center
  .image-block
    display: flex
    justify-content: center
.button-wrap
  margin-top:80px
  .back
    cursor: pointer
</style>
