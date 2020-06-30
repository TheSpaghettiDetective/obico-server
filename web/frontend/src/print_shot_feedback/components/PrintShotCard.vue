<template>
  <div>
    <img class="card-img-top" :src="shot.image_url" />
    <div class="text-center pt-3 px-3">
      <answer-button
        ref="button"
        :checked="shot.answer === consts.LOOKS_BAD"
        :updating="updating && inFlightAnswer === consts.LOOKS_BAD"
        :disabled="updating"
        checked-class="btn-primary"
        @click="looksBad"
      >Yes, I do see spaghetti</answer-button>
      <answer-button
        :checked="shot.answer === consts.LOOKS_OK"
        :updating="updating && inFlightAnswer === consts.LOOKS_OK"
        :disabled="updating"
        checked-class="btn-primary"
        @click="looksOk"
      >No, I do NOT see ANY spaghetti</answer-button>
      <answer-button
        :checked="shot.answer === consts.UNANSWERED"
        :updating="updating && inFlightAnswer === consts.UNANSWERED"
        :disabled="updating"
        checked-class="btn-primary"
        @click="willDecideLater"
      >Hmmm, I am not sure</answer-button>
    </div>
    <div class="float-right text-muted px-2 pb-2">
      Not sure? Look at
      <a
        href="https://www.thespaghettidetective.com/docs/how-does-credits-work/#spaghetti-examples"
      >some examples >>></a>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import apis from '../../lib/apis'
import AnswerButton from './AnswerButton'

const consts = {
  LOOKS_OK: 'LOOKS_OK',
  LOOKS_BAD: 'LOOKS_BAD',
  UNANSWERED: 'UNDECIDED'
}

export default {
  name: 'PrintShotCard',

  components: {
    AnswerButton
  },

  created() {
    this.consts = consts
  },

  props: {
    shot: Object
  },

  computed: {
    updating() {
      return Boolean(this.inFlightAnswer)
    }
  },

  data() {
    return {
      inFlightAnswer: null
    }
  },

  methods: {
    looksOk() {
      this.updateShot(consts.LOOKS_OK)
    },

    looksBad() {
      this.updateShot(consts.LOOKS_BAD)
    },

    willDecideLater() {
      this.updateShot(consts.UNANSWERED)
    },

    updateShot: function(answer) {
      this.inFlightAnswer = answer

      axios
        .put(apis.printShotFeedback(this.shot.id, this.shot.print_id), {
          answer: answer
        })

        .then(response => {
          const { instance, credited_dhs } = response.data
          this.$emit('shotChanged', instance)
          if (credited_dhs > 0) {
            this.$swal({
              title: 'You are awesome!',
              html:
                '<p>The Detective just got a little smarter because of your feedback!</p><p>You just earned 2 non-expirable Detective Hours - Yay!</p>',
              confirmButtonText: 'I\'m done!',
              showCancelButton: true,
              cancelButtonText: 'Change feedback'
            }).then(result => {
              if (result.isConfirmed) {
                window.location.href = '/prints/'
              }
            })
          }
        })

        .finally(() => {
          this.inFlightAnswer = null
        })
    }
  }
}
</script>

<style></style>
