<template>
  <div>
    <img class="card-img-top" :src="shot.image_url" />
    <div class="px-3 pt-4">
      <b-form-group label="Do you see any spaghetti in this picture?">
        <b-form-radio-group
          v-model="answer"
          :options="options"
          @change="updateShot"
        ></b-form-radio-group>
      </b-form-group>
      <small class="text-muted">
        {{$t("Not sure? Look at")}}
        <a
          target="_blank"
          :href="getDocUrl('/user-guides/how-does-credits-work#spaghetti-examples')"
          >{{ $t("some examples. ") }}<small><i class="fas fa-external-link-alt"></i></small
        ></a>
      </small>
      <div class="navigation-container my-4" style="display: flex">
        <b-button variant="outline-secondary" @click="$emit('prev')">
          <i class="fas fa-chevron-left"></i>&nbsp;&nbsp;{{$t("Previous")}}
        </b-button>

        <b-button variant="outline-secondary" @click="$emit('next')">
          {{$t("Next")}}&nbsp;&nbsp;<i class="fas fa-chevron-right"></i>
        </b-button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import urls from '@config/server-urls'
import { BFormGroup, BFormRadioGroup } from 'bootstrap-vue'

export default {
  name: 'PrintShotCard',

  components: {
    BFormGroup,
    BFormRadioGroup,
  },

  props: {
    shot: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      answer: this.shot.answer,
      options: [
        { text: 'Yes', value: 'LOOKS_BAD' },
        { text: 'No', value: 'LOOKS_OK' },
        { text: 'I am not sure', value: 'UNDECIDED' },
      ],
    }
  },

  methods: {
    updateShot: function (answer) {
      axios
        .put(urls.printShotFeedback(this.shot.id, this.shot.print_id), {
          answer: answer,
        })

        .then((response) => {
          const { instance, credited_dhs } = response.data

          if (credited_dhs > 0) {
            this.$swal.Prompt.fire({
              title: `${this.$i18next.t('You are awesome!')}`,
              html: `<p>${this.$i18next.t("The AI failure detection just got a little better because of your feedback!")}</p><p>${this.$i18next.t("You just earned 2 non-expirable AI Detection Hours - Yay!")}</p>`,
              confirmButtonText: `${this.$i18next.t("I'm done!")}`,
              showCancelButton: true,
              cancelButtonText: `${this.$i18next.t('Change feedback')}`,
            }).then((result) => {
              if (result.isConfirmed) {
                window.location.href = '/print_history/'
              } else {
                this.$emit('shotChanged', instance)
              }
            })
          } else {
            this.$emit('shotChanged', instance)
          }
        })
    },
  },
}
</script>

<style lang="sass" scoped>
.navigation-container
  display: flex
  justify-content: space-between
  align-items: center
  gap: 1rem
  margin: -1.5em
  margin-bottom: .5em
  padding: 1em 1.5em
  background-color: var(--color-surface-primary)
</style>
