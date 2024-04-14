<template>
  <b-modal
    id="b-modal-pick-dates"
    :title="$t('Select Dates')"
    :ok-title="$t('Apply')"
    :cancel-title="$t('Cancel')"
    centered
    @ok="handleOk"
    @hidden="resetModal"
    @shown="focusInput"
  >
    <form @submit.prevent="handleSubmit">
      <div class="my-2">
        <b-form-group
          :label="$t('Date from')"
          label-for="date_from"
          :description="$t('If empty, will default to your registration date')"
        >
          <b-form-input
            id="date_from"
            ref="dateFrom"
            v-model="dateFrom"
            type="date"
            :placeholder="$t('Enter date')"
          ></b-form-input>
        </b-form-group>

        <b-form-group
          :label="$t('Date to')"
          label-for="date_to"
          :description="$t('If empty, will default to today')"
        >
          <b-form-input
            id="date_to"
            ref="dateTo"
            v-model="dateTo"
            type="date"
            :placeholder="$t('Enter date')"
          ></b-form-input>
        </b-form-group>

        <b-alert v-if="errorMessage" variant="danger" class="mt-3" show>
          {{ errorMessage }}
        </b-alert>
      </div>
    </form>
  </b-modal>
</template>

<script>
export default {
  name: 'DatePickerModal',

  data() {
    return {
      dateFrom: '',
      dateTo: '',
      isOpen: false,
      errorMessage: '',
    }
  },

  methods: {
    show(initDateFrom, initDateTo) {
      this.dateFrom = initDateFrom || ''
      this.dateTo = initDateTo || ''

      this.isOpen = true
      this.$bvModal.show('b-modal-pick-dates')
    },
    focusInput() {
      this.$refs.dateFrom.select()
    },
    close() {
      this.$bvModal.hide('b-modal-pick-dates')
      this.resetModal()
    },
    resetModal() {
      this.isOpen = false
      this.errorMessage = ''
    },
    handleOk(bvModalEvent) {
      bvModalEvent.preventDefault()
      this.handleSubmit()
    },
    async handleSubmit() {
      if (!this.dateFrom && !this.dateTo) {
        this.errorMessage = `${this.$i18next.t('At least one date is needed')}`
        return
      }

      this.$emit('picked', this.dateFrom, this.dateTo)
      this.$nextTick(() => {
        this.close()
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.input-lg
  height: 3rem
  padding: .5rem 1rem
  width: 100%
</style>
