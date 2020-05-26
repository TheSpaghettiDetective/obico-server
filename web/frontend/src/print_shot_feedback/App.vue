<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <card v-if="loading">
        <div class="card-body">
          <div class="text-center">
            <i class="fas fa-spinner fa-spin" />
            Loading...
          </div>
        </div>
      </card>

      <card v-if="currentShot && !loading">
        <div class="card-header">
          <div class="clearfix">
            <div class="float-left">
              Feedback for #{{ currentIndex + 1 }} of
              <strong>{{ this.shots.length }}</strong>
            </div>
            <div class="float-right">
              <strong v-if="progress == 100">All answered!</strong>
              <strong v-if="progress != 100">{{ progress }}% answered</strong>
            </div>
          </div>
          <progress-bar
            class="clearfix"
            :max="100"
            :value="progress"
          >
            {{ progress }} %
          </progress-bar>
        </div>
        <div class="current-shot-container">
          <img
            class="card-img-top"
            @click="next"
            :src="currentShot.image_url"
          >
          <button
            if-v="currentIndex !== prevIndex"
            class="prev-btn btn btn-primary"
            :disabled="updating"
            @click="prev"
          >
            <i class="fas fa-lg fa-angle-left" />
          </button>
          <button
            if-v="currentIndex !== nextIndex"
            class="next-btn btn btn-primary"
            :disabled="updating"
            @click="next"
          >
            <i class="fas fa-lg fa-angle-right" />
          </button>
        </div>
        <div class="card-body">
          <div class="text-center">
            <answer-button
              ref="button"
              :checked="currentShot.answer === consts.LOOKS_BAD"
              :updating="inFlightAnswer === consts.LOOKS_BAD && updating"
              :disabled="updating"
              checked-class="btn-danger"
              @click="looksBad"
            >
              It contains spaghetti
            </answer-button>
            <answer-button
              :checked="currentShot.answer === consts.LOOKS_OK"
              :updating="inFlightAnswer === consts.LOOKS_OK && updating"
              :disabled="updating"
              checked-class="btn-success"
              @click="looksOk"
            >
              It does NOT contain spaghetti
            </answer-button>
            <answer-button
              :checked="currentShot.answer === consts.UNANSWERED"
              :updating="inFlightAnswer === consts.UNANSWERED && updating"
              :disabled="updating"
              checked-class="btn-warning"
              @click="willDecideLater"
            >
              I'll decide later
            </answer-button>
          </div>
        </div>
      </card>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  import AnswerButton from './components/AnswerButton.vue'
  import ProgressBar from './components/ProgressBar.vue'
  import Card from './components/Card.vue'

  const printShotFeedbackListUrl = printId => `/api/v1/printshotfeedback/?print_id=${printId}`
  const printShotFeedbackUrl = shotId => `/api/v1/printshotfeedback/${shotId}/`

  const consts = {
    LOOKS_OK: 'LOOKS_OK',
    LOOKS_BAD: 'LOOKS_BAD',
    UNANSWERED: '',
  }

  export default {
    name: "App",
    components: {
      AnswerButton,
      Card,
      ProgressBar,
    },
    props: {
      config: {
        default: () => {},
        type: Object,
      },
    },
    data: function() {
      return {
        currentShotId: null,
        loading: true,
        imageLoading : true,
        updating: false,
        inFlightAnswer: null,
        shots: [],
      }
    },
    computed: {
      currentIndex() {
        const currentShotId = this.currentShotId

        if (currentShotId === null || this.shots.length < 1) {
          return null
        }

        return this.shots.findIndex((item) => currentShotId == item.id)
      },

      currentShot() {
        const index = this.currentIndex

        if (index === null) {
          return null
        }

        return this.shots[index]
      },

      prevIndex() {
        const index = this.currentIndex

        if (index === null) {
          return null
        }

        return index == 0 ? this.shots.length - 1 : index - 1
      },

      nextIndex() {
        const index = this.currentIndex

        if (index === null) {
          return null
        }

        return index + 1 >= this.shots.length ? 0 : index + 1
      },
      progress() {
        let answered = this.shots.filter((shot) => shot.answer !== null).length
        let total = this.shots.length
        return parseInt((answered / total) * 100)
      }
    },

    created() {
      this.consts = consts
    },

    mounted() {
      this.fetchShots()

      this.$el.addEventListener('keydown', (e) => {
        if (this.updating) {
          return
        }

        switch (e.key) {
          case 'ArrowLeft':
            this.prev()
            break

          case 'ArrowRight':
            this.next()
            break

          default:
            break
        }
      })
    },
    methods: {
      looksOk() {
        this.updateShot(this.currentShotId, consts.LOOKS_OK)
      },

      looksBad() {
        this.updateShot(this.currentShotId, consts.LOOKS_BAD)
      },

      willDecideLater() {
        this.updateShot(this.currentShotId, '')
      },

      next() {
        if (this.nextIndex !== null) {
          this.currentShotId = this.shots[this.nextIndex].id
        }
      },

      prev() {
        if (this.prevIndex !== null) {
          this.currentShotId = this.shots[this.prevIndex].id
        }
      },

      fetchShots() {
        this.loading = true

        axios
          .get(printShotFeedbackListUrl(this.config.printId))

          .then((response) => {
            this.shots = response.data
            this.shots.forEach((item) => {
              item.answer = item.answer === consts.UNANSWERED ? null : consts.UNANSWERED
            })

            if (this.shots.length > 0) {
              this.currentShotId = this.shots[0].id
            }
          })

          .catch((error) => {
            console.log(error)
            this.$swal('Ops', 'Something went wrong!', 'error').then(() => location.reload())
          })

          .finally(() => {
            this.loading = false
          })
      },

      updateShot: function(id, answer) {
        this.updating = true
        this.inFlightAnswer = answer

        axios
          .put(printShotFeedbackUrl(id), { answer: answer })

          .then((response) => {
            this.shots = this.shots.map((shot) => {
              return shot.id === response.data.id ? response.data : shot
            })
          })

          .catch(() => {
            this.$swal('Ops', 'Could not save answer! Please retry!', 'error')
          })

          .finally(() => {
            this.updating = false
            this.inFlightAnswer = null
          })
      },
    },
  }
</script>

<style>
  .printshots-container {
    margin-top: 1.5em;
  }

  .current-shot-container {
    position: relative;
  }

  .prev-btn {
    display: inline;
    position: absolute;
    left: 2%;
    top: 40%;
    opacity: 0.5;
  }

  .next-btn {
    display: inline;
    position: absolute;
    right: 2%;
    top: 40%;
    opacity: 0.5;
  }
</style>
