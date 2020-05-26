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
          <div class="float-left">
            Displaying Shot #{{ currentIndex + 1 }}
          </div>
          <div class="float-right">
            <strong>{{ this.shots.length }}</strong> shots in total
          </div>
        </div>
        <div class="current-shot-container">
          <img
            v-if="currentShot.image_url"
            class="card-img-top"
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
  import AnswerButton from './components/AnswerButton.vue';
  import Card from './components/Card.vue';
  const axios = require('axios');

  function printShotFeedbackListUrl(print_id) {
    return `/api/v1/printshotfeedback/?print_id=${print_id}`;
  }

  function printShotFeedbackUrl(id) {
    return `/api/v1/printshotfeedback/${id}/`;
  }

  const consts = {
    LOOKS_OK: 'LOOKS_OK',
    LOOKS_BAD: 'LOOKS_BAD',
    UNANSWERED: '',
  };

  export default {
    name: "App",
    components: {
      AnswerButton,
      Card,
    },
    props: {
      config: {
        default: function() {
          return {};
        },
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
      };
    },
    computed: {
      currentIndex: function() {
        const currentShotId = this.currentShotId;

        if (currentShotId === null || this.shots.length < 1) {
          return null;
        }

        return this.shots.findIndex(function(item) {
          return currentShotId == item.id;
        });
      },
      currentShot: function() {
        const index = this.currentIndex;
        if (index === null) {
          return null;
        }
        return this.shots[index];
      },
      prevIndex: function() {
        const index = this.currentIndex;

        if (index === null) {
          return null;
        }

        return index == 0 ? this.shots.length - 1 : index - 1;
      },
      nextIndex: function() {
        const index = this.currentIndex;

        if (index === null) {
          return null;
        }

        return index + 1 >= this.shots.length ? 0 : index + 1;
      },
    },
    created: function() {
      this.consts = consts;
    },
    mounted: function() {
      var vm = this;

      this.fetchShots();

      this.$el.addEventListener('keydown', function(e) {
        if (vm.updating) {
          return;
        }
        switch (e.key) {
          case 'ArrowLeft':
            vm.prev();
            break;
          case 'ArrowRight':
            vm.next();
            break;
          default:
            break;
        }
      });
    },
    methods: {
      looksOk: function() {
        this.updateShot(this.currentShotId, consts.LOOKS_OK);
      },
      looksBad: function() {
        this.updateShot(this.currentShotId, consts.LOOKS_BAD);
      },
      willDecideLater: function() {
        this.updateShot(this.currentShotId, '');
      },
      next: function() {
        if (this.nextIndex !== null) {
          this.currentShotId = this.shots[this.nextIndex].id;
        }
      },
      prev: function() {
        if (this.prevIndex !== null) {
          this.currentShotId = this.shots[this.prevIndex].id;
        }
      },
      fetchShots: function() {
        this.loading = true;
        var vm = this;
        axios
          .get(printShotFeedbackListUrl(this.config.printId))
          .then(function(response) {
            vm.shots = response.data;
            if (vm.shots.length > 0) {
              vm.currentShotId = vm.shots[0].id;
            }
          })
          .catch(function(error) {
            console.log(error);
            vm.$swal('Ops', 'Something went wrong!', 'error').then(function() {
              location.reload();
            });
          })
          .finally(function() {
            vm.loading = false;
          });
      },

      updateShot: function(id, answer) {
        this.updating = true;
        this.inFlightAnswer = answer;
        var vm = this;
        axios
          .put(printShotFeedbackUrl(id), { answer: answer })
          .then(function(response) {
            vm.shots = vm.shots.map(function(shot) {
              return shot.id === response.data.id ? response.data : shot;
            });
          })
          .catch(function() {
            vm.$swal('Ops', 'Could not save answer! Please retry!', 'error');
          })
          .finally(function() {
            vm.updating = false;
            vm.inFlightAnswer = null;
          });
      },
    },
  };
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
