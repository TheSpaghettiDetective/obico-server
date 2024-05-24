<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row class="justify-content-center">
          <b-col lg="8">
            <loading-placeholder v-if="!printer" />
            <div v-else class="surface with-loading-animation full-on-mobile">
              <section class="settings">
                <h2 class="section-title">{{ $t("Settings") }}</h2>
                <div class="form-group mb-4 mt-4">
                  <div class="form-label text-muted mb-2">{{ $t("Give your shiny new printer a name") }}</div>
                  <saving-animation :errors="errorMessages.name" :saving="saving.name">
                    <input
                      id="id_name"
                      v-model="printer.name"
                      type="text"
                      name="name"
                      maxlength="200"
                      placeholder=""
                      class="form-control field_required"
                      required="required"
                    />
                  </saving-animation>
                </div>
                <!-- Potential failure section -->
                <div class="failure-notification">
                  <div class="form-group mt-4 mb-4">
                    <div class="form-label text-muted">{{ $t("When a potential failure is detected") }}:</div>
                    <saving-animation
                      :errors="errorMessages.action_on_failure_NONE"
                      :saving="saving.action_on_failure_NONE"
                    >
                      <div class="custom-control custom-radio mt-1 radio">
                        <input
                          id="id_action_on_failure_0"
                          v-model="printer.action_on_failure"
                          type="radio"
                          name="action_on_failure"
                          class="custom-control-input field_required"
                          value="NONE"
                          @change="updateSetting('action_on_failure')"
                        />
                        <label class="custom-control-label" for="id_action_on_failure_0"
                          >{{ $t("Just notify me") }}</label
                        >
                      </div>
                    </saving-animation>
                    <saving-animation
                      :errors="errorMessages.action_on_failure_PAUSE"
                      :saving="saving.action_on_failure_PAUSE"
                    >
                      <div
                        id="action_on_failure_PAUSE"
                        class="custom-control custom-radio mt-1 radio"
                      >
                        <input
                          id="id_action_on_failure_1"
                          v-model="printer.action_on_failure"
                          type="radio"
                          name="action_on_failure"
                          class="custom-control-input field_required"
                          value="PAUSE"
                          @change="updateSetting('action_on_failure')"
                        />
                        <label class="custom-control-label" for="id_action_on_failure_1"
                          >{{ $t("Pause the printer and notify me") }}</label
                        >
                      </div>
                    </saving-animation>
                  </div>
                </div>
              </section>
              <section class="mt-5">
                <h2 class="section-title">{{ $t("Failure Detection") }}</h2>
                <div class="card-body p-0 pt-3">
                  <p class="text-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    {{$t("If you are not sure about the settings below, leave the default values to minimize surprises.")}}
                  </p>

                  <!-- Advanced settngs: when printer is paused -->
                  <div class="form-group mt-4">
                    <div class="form-label text-muted">{{ $t("When print is paused,") }}</div>
                    <saving-animation
                      :errors="errorMessages.tools_off_on_pause"
                      :saving="saving.tools_off_on_pause"
                    >
                      <div class="custom-control custom-checkbox mt-2 checkbox">
                        <input
                          id="id_tools_off_on_pause"
                          v-model="printer.tools_off_on_pause"
                          type="checkbox"
                          name="tools_off_on_pause"
                          class="custom-control-input"
                          @change="updateSetting('tools_off_on_pause')"
                        />
                        <label class="custom-control-label" for="id_tools_off_on_pause">
                          {{$t("Turn off hotend heater(s)")}}
                        </label>
                      </div>
                    </saving-animation>
                    <saving-animation
                      :errors="errorMessages.bed_off_on_pause"
                      :saving="saving.bed_off_on_pause"
                    >
                      <div class="custom-control custom-checkbox mt-2 checkbox">
                        <input
                          id="id_bed_off_on_pause"
                          v-model="printer.bed_off_on_pause"
                          type="checkbox"
                          name="bed_off_on_pause"
                          class="custom-control-input"
                          @change="updateSetting('bed_off_on_pause')"
                        />
                        <label class="custom-control-label" for="id_bed_off_on_pause">
                          {{$t("Turn off bed heater")}}
                        </label>
                      </div>
                    </saving-animation>

                    <saving-animation
                      :errors="errorMessages.retract_on_pause"
                      :saving="saving.retract_on_pause"
                      class="mobile-full-width"
                    >
                      <div class="form-inline my-1 checkbox-with-input">
                        <div class="custom-control custom-checkbox">
                          <input
                            id="retract-checkbox"
                            v-model="retractFilamentByEnabled"
                            type="checkbox"
                            class="custom-control-input"
                          />
                          <label class="custom-control-label" for="retract-checkbox"
                            >{{ $t("Retract filament by") }}</label
                          >
                        </div>
                        <number-input
                          v-model="retractOnPause"
                          :step="0.5"
                          :disable="!retractFilamentByEnabled"
                          class="wrappable-field"
                        ></number-input>
                      </div>
                    </saving-animation>

                    <saving-animation
                      :errors="errorMessages.lift_z_on_pause"
                      :saving="saving.lift_z_on_pause"
                      class="mobile-full-width"
                    >
                      <div class="form-inline my-1 checkbox-with-input">
                        <div class="custom-control custom-checkbox">
                          <input
                            id="lift-z-checkbox"
                            v-model="liftExtruderByEnabled"
                            type="checkbox"
                            class="custom-control-input"
                          />
                          <label class="custom-control-label" for="lift-z-checkbox"
                            >{{ $t("Lift extruder along Z axis by") }}</label
                          >
                        </div>
                        <number-input
                          v-model="liftExtruderBy"
                          :step="0.5"
                          :disable="!liftExtruderByEnabled"
                          class="wrappable-field"
                        ></number-input>
                      </div>
                    </saving-animation>
                  </div>

                  <!-- Advanced settngs: sensitivity slider -->
                  <div class="form-group sensitivity my-4">
                    <div class="form-label text-muted">{{ $t("AI failure detection sensitivity") }}</div>
                    <saving-animation
                      :errors="errorMessages.detective_sensitivity"
                      :saving="saving.detective_sensitivity"
                    >
                      <div class="my-2 sensitivity-slider">
                        <vue-slider
                          v-model="detectiveSensitivity"
                          :lazy="true"
                          :min="0.8"
                          :max="1.2"
                          :interval="0.05"
                          :tooltip-formatter="sensitivityTooltipFormatter"
                        />
                      </div>
                    </saving-animation>
                    <div
                      v-if="sensitivityTooltipFormatter(printer.detective_sensitivity) === 'Low'"
                    >
                      {{$t("Low - I don't want a lot of false alarms. Only alert me when you are absolutely sure.")}}
                    </div>
                    <div
                      v-else-if="
                        sensitivityTooltipFormatter(printer.detective_sensitivity) === 'Medium'
                      "
                    >
                      {{$t("Medium - A few false alarms won't bother me. But some well-disguised spaghetti will be missed.")}}
                    </div>
                    <div v-else>
                      {{$t("High - Hit me with all the false alarms. I want to catch as many failures as possible.")}}
                    </div>
                  </div>
                </div>
              </section>
              <section class="mt-5">
                <h2 class="section-title">{{ $t("Time-lapse") }}</h2>
                <p
                  v-if="!(timelapseOnFinishEnabled && timelapseOnCancelEnabled)"
                  class="text-warning"
                >
                  <i class="fas fa-exclamation-triangle"></i>
                  <i18next :translation="$t(`Focused Feedback won't be available when time-lapse recording is turned off. You won't be able to {localizedDom}`)">
                    <template #localizedDom>
                      <a :href="getDocUrl('/user-guides/how-does-credits-work/')">{{$t("help us get better while earning AI Detection Hours for yourself")}}</a>
                    </template>
                  </i18next>

                </p>
                <div class="form-group mt-4">
                  <saving-animation
                    :errors="errorMessages.min_timelapse_secs_on_finish"
                    :saving="saving.min_timelapse_secs_on_finish"
                    class="mobile-full-width"
                  >
                    <div class="form-inline my-1 checkbox-with-input">
                      <div class="custom-control custom-checkbox">
                        <input
                          id="timelapseOnFinishEnabled"
                          v-model="timelapseOnFinishEnabled"
                          type="checkbox"
                          class="custom-control-input"
                        />
                        <label class="custom-control-label" for="timelapseOnFinishEnabled"
                          >{{ $t("Record time-lapse when a print finishes successfully.") }}</label
                        >
                      </div>
                    </div>
                    <div
                      v-if="timelapseOnFinishEnabled"
                      class="form-inline my-1 checkbox-with-input"
                    >
                      <div class="custom-control custom-checkbox">
                        {{$t("Skip if the print is finished in less than")}}
                      </div>
                      <number-input
                        v-model="minTimelapseMinutesOnFinish"
                        :step="5"
                        unit="minutes"
                        class="wrappable-field"
                      ></number-input>
                    </div>
                  </saving-animation>
                  <saving-animation
                    :errors="errorMessages.min_timelapse_secs_on_cancel"
                    :saving="saving.min_timelapse_secs_on_cancel"
                    class="mobile-full-width"
                  >
                    <div class="form-inline mt-3 mb-1 checkbox-with-input">
                      <div class="custom-control custom-checkbox">
                        <input
                          id="timelapseOnCancelEnabled"
                          v-model="timelapseOnCancelEnabled"
                          type="checkbox"
                          class="custom-control-input"
                        />
                        <label class="custom-control-label" for="timelapseOnCancelEnabled"
                          >{{ $t("Record time-lapse when a print is cancelled.") }}</label
                        >
                      </div>
                    </div>
                    <div
                      v-if="timelapseOnCancelEnabled"
                      class="form-inline my-1 checkbox-with-input"
                    >
                      <div class="custom-control custom-checkbox">
                        {{$t("Skip if the print is cancelled in less than")}}
                      </div>
                      <number-input
                        v-model="minTimelapseMinutesOnCancel"
                        :step="5"
                        unit="minutes"
                        class="wrappable-field"
                      ></number-input>
                    </div>
                  </saving-animation>
                </div>
              </section>
              <section class="danger mt-5">
                <h2 class="section-title">{{ $t("Danger Zone") }}</h2>
                <div class="mt-4">
                  <a class="btn btn-outline-secondary" :href="printerWizardUrl">
                    {{$t("Re-Link Printer")}}
                  </a>
                  <div class="text-muted mt-1">
                    <small>
                      <i18next :translation="$t(`If your printer is always showing as 'offline', and you have gone through {localizedDom}, you can try to re-link printer as the last resort.`)">
                        <template #localizedDom>
                          <a :href="getDocUrl('/user-guides/troubleshoot-server-connection-issues/')">{{$t("all the trouble-shooting steps")}}</a>
                        </template>
                      </i18next>
                    </small>
                  </div>
                </div>
                <div v-if="isEnt" class="mt-4">
                  <button class="btn btn-outline-warning" @click="archivePrinter">
                    {{$t("Archive Printer")}}
                  </button>
                  <div class="text-muted mt-1">
                    <small>
                      <i18next :translation="$t(`Archived printers are not counted toward your subscription plan. You won't see them in the app either. Go to {localizedDom} to find all archived printers and/or un-archive them.`)">
                        <template #localizedDom>
                          <a href="/ent/printers/archived/">{{ $t("this page") }}</a>
                        </template>
                      </i18next>
                      </small>
                  </div>
                </div>
                <div class="mt-4">
                  <button class="btn btn-outline-danger" @click="deletePrinter">
                    {{$t("Delete Printer")}}
                  </button>
                  <div class="text-muted mt-1">
                    <small>{{ $t("Bye-bye printer.") }}</small>
                  </div>
                </div>
              </section>
            </div>
          </b-col>
        </b-row>
      </b-container>

      <!-- <div class="row justify-content-center">
        <div class="col-sm-11 col-md-10 col-lg-8">


        </div>
      </div> -->
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import split from 'lodash/split'
import VueSlider from 'vue-slider-component'

import { normalizedPrinter } from '@src/lib/normalizers'
import urls from '@config/server-urls'
import SavingAnimation from '@src/components/SavingAnimation.vue'
import NumberInput from '@src/components/NumberInput.vue'
import PageLayout from '@src/components/PageLayout.vue'
import { settings } from '@src/lib/page-context'

export default {
  components: {
    SavingAnimation,
    NumberInput,
    PageLayout,
    VueSlider,
  },

  data() {
    return {
      isEnt: false,
      printer: null,
      printerId: '',
      saving: {},
      errorMessages: {},
      delayedSubmit: {
        // Make pause before sending new value to API
        name: {
          delay: 1000,
          timeoutId: null,
        },
        retract_on_pause: {
          delay: 1000,
          timeoutId: null,
        },
        lift_z_on_pause: {
          delay: 1000,
          timeoutId: null,
        },
        min_timelapse_secs_on_finish: {
          delay: 1000,
          timeoutId: null,
        },
        min_timelapse_secs_on_cancel: {
          delay: 1000,
          timeoutId: null,
        },
      },
    }
  },

  computed: {
    retractFilamentByEnabled: {
      get() {
        return this.printer.retract_on_pause > 0
      },
      set(newValue) {
        if (newValue) {
          this.printer.retract_on_pause = 6.5 // Default retraction value
        } else {
          this.printer.retract_on_pause = 0
        }
      },
    },
    retractOnPause: {
      get() {
        return this.printer ? this.printer.retract_on_pause : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.retract_on_pause = newValue
        }
      },
    },
    liftExtruderByEnabled: {
      get() {
        return this.printer.lift_z_on_pause > 0
      },
      set(newValue) {
        if (newValue) {
          this.printer.lift_z_on_pause = 2.5 // Default z-lift value
        } else {
          this.printer.lift_z_on_pause = 0
        }
      },
    },
    liftExtruderBy: {
      get() {
        return this.printer ? this.printer.lift_z_on_pause : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.lift_z_on_pause = newValue
        }
      },
    },
    timelapseOnFinishEnabled: {
      get() {
        return this.printer.min_timelapse_secs_on_finish >= 0
      },
      set(newValue) {
        if (newValue) {
          this.printer.min_timelapse_secs_on_finish = 600
        } else {
          this.printer.min_timelapse_secs_on_finish = -1
        }
      },
    },
    minTimelapseMinutesOnFinish: {
      get() {
        return this.printer ? this.printer.min_timelapse_secs_on_finish / 60 : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.min_timelapse_secs_on_finish = newValue * 60
        }
      },
    },
    timelapseOnCancelEnabled: {
      get() {
        return this.printer.min_timelapse_secs_on_cancel >= 0
      },
      set(newValue) {
        if (newValue) {
          this.printer.min_timelapse_secs_on_cancel = 300
        } else {
          this.printer.min_timelapse_secs_on_cancel = -1
        }
      },
    },
    minTimelapseMinutesOnCancel: {
      get() {
        return this.printer ? this.printer.min_timelapse_secs_on_cancel / 60 : undefined
      },
      set(newValue) {
        if (this.printer) {
          this.printer.min_timelapse_secs_on_cancel = newValue * 60
        }
      },
    },
    printerWizardUrl() {
      return urls.printerWizard(this.printer.id)
    },
    printerName: {
      get: function () {
        return this.printer ? this.printer.name : undefined
      },
      set: function (newValue) {
        this.printer.name = newValue
      },
    },
    detectiveSensitivity: {
      get() {
        return this.printer.detective_sensitivity
      },
      set(newValue) {
        this.printer.detective_sensitivity = newValue
        this.updateSetting('detective_sensitivity')
      },
    },
  },

  // Watch these properties so that updates can be triggered at key-press, instead of losing focus
  // To watch deep properties in an object: https://stackoverflow.com/questions/42133894/vue-js-how-to-properly-watch-for-nested-data
  watch: {
    printerName: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('name')
      }
    },
    retractOnPause: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.changeRetractOnPause(newValue)
      }
    },
    liftExtruderBy: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.changeLiftExtruderBy(newValue)
      }
    },
    minTimelapseMinutesOnFinish: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('min_timelapse_secs_on_finish')
      }
    },
    minTimelapseMinutesOnCancel: function (newValue, oldValue) {
      if (oldValue !== undefined) {
        this.updateSetting('min_timelapse_secs_on_cancel')
      }
    },
  },

  created() {
    const { IS_ENT } = settings()
    this.isEnt = !!IS_ENT
    this.printerId = split(window.location.pathname, '/').slice(-2, -1).pop()
    this.fetchPrinter()
  },

  methods: {
    /**
     * Get actual printer settings
     */
    fetchPrinter() {
      return axios
        .get(urls.printer(this.printerId))
        .then((response) => {
          this.printer = normalizedPrinter(response.data, this.printer)
        })
        .catch((error) => {
          this.errorDialog(error, `${this.$i18next.t('Printer not found')}`)
        })
    },

    /**
     * Update printer settings
     * @param {String} propName
     * @param {any} propValue
     * @param {String} settingsItem
     */
    patchPrinter(propName, propValue) {
      const inputElem = this.getSettingsItemInput(propName, propValue)
      this.setSavingStatus(inputElem, true)

      // Make request to API
      return axios
        .patch(urls.printer(this.printerId), {
          [propName]: propValue,
        })
        .catch((err) => {
          if (err.response && err.response.data && typeof err.response.data === 'object') {
            if (err.response.data.non_field_errors) {
              this.errorAlert(err.response.data.non_field_errors)
            } else {
              for (const error in err.response.data) {
                this.errorMessages[inputElem] = err.response.data[error]
              }
            }
          } else {
            this.errorAlert()
          }
        })
        .then(() => {
          this.setSavingStatus(inputElem, false)
        })
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert() {
      this.$swal.Toast.fire({
        icon: 'error',
        html: `<div>${this.$i18next.t("Can not update printer settings.")}</div><div>${this.$i18next.t("Get help from")} <a href="https://obico.io/discord">${this.$i18next.t("the {brandName} general support forum",{brandName:this.$syndicateText.brandName})}</a> ${this.$i18next.t("or")} <a href="https://obico.io/discord">${this.$i18next.t("{brandName} for klipper support forum",{brandName:this.$syndicateText.brandName})}</a> ${this.$i18next.t("if this error persists.")}</div>`,
      })
    },

    /**
     * Update particular settings item
     * @param {String} settingsItem
     */
    updateSetting(settingsItem) {
      if (settingsItem in this.delayedSubmit) {
        const delayInfo = this.delayedSubmit[settingsItem]
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }
        this.delayedSubmit[settingsItem]['timeoutId'] = setTimeout(() => {
          this.patchPrinter(settingsItem, this.printer[settingsItem])
        }, delayInfo['delay'])
        return
      }

      this.patchPrinter(settingsItem, this.printer[settingsItem])
    },

    sensitivityTooltipFormatter: function (value) {
      if (value < 0.95) {
        return 'Low'
      }
      if (value > 1.05) {
        return 'High'
      }
      return 'Medium'
    },

    deletePrinter(printer) {
      this.$swal.Prompt.fire({
        title: `${this.$i18next.t('Are you sure?')}`,
        text: `${this.$i18next.t(`Delete {name} printer? This action can not be undone.`,{name:this.printer.name})}`,
        showCancelButton: true,
        confirmButtonText: `${this.$i18next.t('Yes')}`,
        cancelButtonText: `${this.$i18next.t('No')}`,
      }).then((userAction) => {
        if (userAction.isConfirmed) {
          axios.delete(urls.printer(this.printerId) + '?with_archived=true').then(() => {
            window.location.href = `/printers/`
          })
        }
      })
    },

    archivePrinter() {
      this.$swal.Confirm.fire().then((userAction) => {
        if (userAction.isConfirmed) {
          axios.post(urls.printerAction(this.printerId, '/archive/')).then(() => {
            this.$swal.Prompt.fire({
              title: `${this.$i18next.t('Printer archived')}`,
              html: `<p>${this.$i18next.t("{name} is archived.",{name:this.printer.name})}</p><p>${this.$i18next.t("You can find it on")} <a href="/ent/printers/archived/">${this.$i18next.t("this page")}</a> ${this.$i18next.t("and un-archive it")}.</p>`,
              confirmButtonText: `${this.$i18next.t('Go to the printer page')}`,
            }).then(() => {
              window.location.href = '/printers/'
            })
          })
        }
      })
    },

    /**
     * Return input element by given name
     * @param {String} settingsItem
     * @returns {Object, null}
     */
    getSettingsItemInput: function (settingsItem, value = '') {
      switch (settingsItem) {
        case 'action_on_failure':
          return `${settingsItem}_${value}`
        default:
          return `${settingsItem}`
      }
    },

    /**
     * Interlayer for saving status control to be able to set same saving status
     * for 2 or more different inputs grouped to one block
     * @param {String} propName
     * @param {String} status
     */
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },

    changeRetractOnPause(value) {
      this.printer.retract_on_pause = value
      this.updateSetting('retract_on_pause')
    },

    changeLiftExtruderBy(value) {
      this.printer.lift_z_on_pause = value
      this.updateSetting('lift_z_on_pause')
    },
  },
}
</script>

<style lang="sass" scoped>
@import 'vue-slider-component/lib/theme/default.scss'

.card
  overflow: visible !important

.custom-control-label
  font-size: 16px

@media (max-width: 768px)
  .mobile-full-width
    width: 100%
    margin-top: .25em
    margin-bottom: .4em

.section-title
  padding-bottom: 10px
  border-bottom: 1px solid var(--color-text-primary)

.form-label
  font-size: 18px

section.danger
  .section-title
    color: var(--color-danger)
    border-color: var(--color-danger)

.form-inline
  .wrappable-field
    margin-left: 1.5rem
</style>
