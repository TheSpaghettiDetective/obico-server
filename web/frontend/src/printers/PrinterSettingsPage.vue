<template>
<div class="row justify-content-center">
  <div class="col-sm-12 col-md-10 col-lg-8 settings-container">
    <section class="settings">
      <h2 class="section-title">Settings</h2>
      <div class="form-group mb-4 mt-4">
        <div class="form-label text-muted mb-2">Give your shiny new printer a name</div>
        <form @submit.prevent="newPrinterName" id="printerNameForm">
          <input
            id="printerName"
            type="text"
            name="name"
            v-model="printerName"
            maxlength="200"
            placeholder="My Awesome 3D Printer"
            class="form-control field_required"
            required="required">
            <small class="text-muted">Click Enter to save new name</small>
        </form>
      </div>

      <PrinterPreferences
        ref="PrinterPreferences"

        :pauseAndNotify="pauseAndNotify"
        :isHotendHeaterOff="advancedSettings.isHotendHeaterOff"
        :isBedHeaterOff="advancedSettings.isBedHeaterOff"
        :retractFilamentBy="advancedSettings.retractFilamentBy"
        :liftExtruderBy="advancedSettings.liftExtruderBy"
        :sensitivity="advancedSettings.sensitivity"

        @pauseAndNotifyChanged="pauseAndNotifyChanged"
        @isHotendHeaterOffChanged="isHotendHeaterOffChanged"
        @isBedHeaterOffChanged="isBedHeaterOffChanged"
        @retractFilamentByChanged="retractFilamentByChanged"
        @liftExtruderByChanged="liftExtruderByChanged"
        @sensitivityChanged="sensitivityChanged"/>
    </section>
    <section class="danger mt-5">
      <h2 class="section-title">Danger Zone</h2>
      <div class="text-center mt-4">
        <button
          class="btn btn-outline-danger"
          @click="deletePrinter"
        >
          Delete Printer
        </button>
      </div>
    </section>
  </div>
</div>
</template>

<script>
import axios from 'axios'

import { normalizedPrinter } from '@lib/normalizers'
import urls from '@lib/server_urls'
import PrinterPreferences from '../printers/PrinterPreferences'

export default {
  components: {
    PrinterPreferences
  },

  data() {
    return {
      printer: null,
      loading: false,
      printerName: 'Epson',
      pauseAndNotify: true, // true, false (settings: When a potential failure is detected)
      advancedSettings: {
        isHotendHeaterOff: true, // true, false
        isBedHeaterOff: false, // true, false
        retractFilamentBy: false, // false or number (in string format) from 0 with 0.5 step
        liftExtruderBy: '2.5', // false or number (in string format) from 0 with 0.5 step
        sensitivity: '1', // number (in string format) from 0.8 to 1.2 with 0.05 step
      }
    }
  },

  mounted() {
    const printerId = (new URLSearchParams(window.location.search)).get('printerId')
    this.fetchPrinter(printerId)
  },

  methods: {
    fetchPrinter(printerId) {
      this.loading = true
      return axios
        .get(urls.printer(printerId))
        .then(response => {
          this.loading = false
          this.printer = normalizedPrinter(response.data)
        })
    },

    /**
     * Show animation of successful settings save
     * @param {String} inputName
     */
    successfullySavedFeedback(inputName) {
      let elem

      switch (inputName) {
        case 'printerName':
          elem = document.querySelector('#printerNameForm')
          break
        default:
          return
      }

      elem.classList.remove('loading')
      elem.classList.add('successfully-saved')
      setTimeout(
        () => elem.classList.remove('successfully-saved'),
        800
      )
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert() {
      this.$swal('Error occured!', '<p class="text-center">Can not save your new settings, please try again.</p>', 'error')
    },

    /**
     * Printer name is changed - call the API
     */
    newPrinterName() {
      const newName = document.querySelector('#printerName').value
      if (newName) {
        // TODO: call API
        document.querySelector('#printerNameForm').classList.add('loading')
        setTimeout(() => {
          this.successfullySavedFeedback('printerName')
        }, 1000)
      }
    },

    /**
     * Settings change emits from child PrinterPreferences component
     */

    pauseAndNotifyChanged(value) {
      this.pauseAndNotify = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        this.$refs.PrinterPreferences.successfullySavedFeedback('pauseAndNotify', value)
      }, 1000)
    },
    isHotendHeaterOffChanged(value) {
      this.advancedSettings.isHotendHeaterOff = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        this.$refs.PrinterPreferences.successfullySavedFeedback('isHotendHeaterOff', value)
      }, 1000)
    },
    isBedHeaterOffChanged(value) {
      this.advancedSettings.isBedHeaterOff = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        // Example of error alert
        this.$refs.PrinterPreferences.clearAPICallAnimation('isBedHeaterOff', value)
        this.errorAlert()
      }, 1000)
    },
    retractFilamentByChanged(value) {
      this.advancedSettings.retractFilamentBy = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        this.$refs.PrinterPreferences.successfullySavedFeedback('retractFilamentBy', value)
      }, 1000)
    },
    liftExtruderByChanged(value) {
      this.advancedSettings.liftExtruderBy = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        this.$refs.PrinterPreferences.successfullySavedFeedback('liftExtruderBy', value)
      }, 1000)
    },
    sensitivityChanged(value) {
      this.advancedSettings.sensitivity = value
      console.log(value)
      // TODO: call API
      setTimeout(() => {
        this.$refs.PrinterPreferences.successfullySavedFeedback('sensitivity', value)
      }, 1000)
    },
    deletePrinter() {
      this.$swal.Confirm.fire().then((result) => {
        if (result.value) {
          console.log('Delete printer')
          // TODO: delete printer
        }
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.settings-container
  margin: 2em 0em
  padding: 2em 3em
  background: theme.$body-bg
  -webkit-box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.3) !important
  border: none !important

.section-title
  padding-bottom: 5px
  border-bottom: 1px solid theme.$white

.form-label
  font-size: 18px

section.danger
  .section-title
    color: theme.$danger
    border-color: theme.$danger

// API call animation
#printerNameForm
  $indicatorSize: 16px

  &:before
    content: ""
    background-size: $indicatorSize $indicatorSize
    width: $indicatorSize
    height: $indicatorSize
    display: block
    position: absolute
    top: 10px
    right: -#{$indicatorSize + 16px}
    margin: auto
    z-index: 9

  &.loading
    position: relative

    &:before
      background-image: url('/static/img/tail-spin.svg')

  &.successfully-saved
    position: relative

    &:before
      background-image: url('/static/img/tick.svg')
</style>
