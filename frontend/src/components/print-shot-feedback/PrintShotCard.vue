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
        Not sure? Look at
        <a target="_blank"
          href="https://www.obico.io/docs/user-guides/how-does-credits-work#spaghetti-examples"
        >some examples. <small><i class="fas fa-external-link-alt"></i></small></a>
      </small>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import urls from '@config/server-urls'
import { BFormGroup, BFormRadioGroup} from 'bootstrap-vue'

export default {
  name: 'PrintShotCard',

  components: {
    BFormGroup,
    BFormRadioGroup,
  },

  props: {
    shot: Object
  },

  data() {
    return {
      answer: this.shot.answer,
      options: [
        { text: 'Yes', value: 'LOOKS_BAD' },
        { text: 'No', value: 'LOOKS_OK' },
        { text: 'I am not sure', value: 'UNDECIDED' },
      ]
    }
  },

  methods: {
    updateShot: function(answer) {
      axios
        .put(urls.printShotFeedback(this.shot.id, this.shot.print_id), {
          answer: answer
        })

        .then(response => {
          const { instance, credited_dhs } = response.data

          if (credited_dhs > 0) {
            this.$swal.Prompt.fire({
              title: 'You are awesome!',
              html:
                '<p>The AI failure detection just got a little better because of your feedback!</p><p>You just earned 2 non-expirable AI Detection Hours - Yay!</p>',
              confirmButtonText: 'I\'m done!',
              showCancelButton: true,
              cancelButtonText: 'Change feedback'
            }).then(result => {
              if (result.isConfirmed) {
                window.location.href = '/prints/'
              } else {
                this.$emit('shotChanged', instance)
              }
            })
          } else {
            this.$emit('shotChanged', instance)
          }
        })
    }
  }
}
</script>

<style></style>
