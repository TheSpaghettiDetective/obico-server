<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <entrance
        v-if="!consented"
        :print="this.print"
        @continue-btn-pressed="continueBtnPressed = true"
      />
      <card v-if="currentShot && consented">
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
          <progress-bar class="clearfix" :max="100" :value="progress">{{ progress }} %</progress-bar>
        </div>
        <div class="current-shot-container">
          <img class="card-img-top" @click="next" :src="currentShot.image_url" />
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
            >It contains spaghetti</answer-button>
            <answer-button
              :checked="currentShot.answer === consts.LOOKS_OK"
              :updating="inFlightAnswer === consts.LOOKS_OK && updating"
              :disabled="updating"
              checked-class="btn-success"
              @click="looksOk"
            >It does NOT contain spaghetti</answer-button>
            <answer-button
              :checked="currentShot.answer === consts.UNANSWERED"
              :updating="inFlightAnswer === consts.UNANSWERED && updating"
              :disabled="updating"
              checked-class="btn-warning"
              @click="willDecideLater"
            >I'll decide later</answer-button>
          </div>
        </div>
      </card>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import find from "lodash/find";
import get from "lodash/get";

import AnswerButton from "./components/AnswerButton.vue";
import ProgressBar from "./components/ProgressBar.vue";
import Entrance from "./components/Entrance";
import Card from "../common/Card.vue";

const printShotFeedbackListUrl = printId =>
  `/api/v1/printshotfeedbacks/?print_id=${printId}`;
const printShotFeedbackUrl = shotId => `/api/v1/printshotfeedbacks/${shotId}/`;
const printUrl = printId => `/api/v1/prints/${printId}/`;

const consts = {
  LOOKS_OK: "LOOKS_OK",
  LOOKS_BAD: "LOOKS_BAD",
  UNANSWERED: "",
  UNSET: null
};

export default {
  name: "App",
  components: {
    AnswerButton,
    Card,
    ProgressBar,
    Entrance
  },
  props: {
    config: {
      default: () => {},
      type: Object
    }
  },
  data: function() {
    return {
      currentShotId: null,
      imageLoading: true,
      updating: false,
      inFlightAnswer: null,
      shots: [],
      print: null,
      continueBtnPressed: false
    };
  },
  computed: {
    currentIndex() {
      const currentShotId = this.currentShotId;

      if (currentShotId === null || this.shots.length < 1) {
        return null;
      }

      return this.shots.findIndex(item => currentShotId == item.id);
    },

    currentShot() {
      const index = this.currentIndex;

      if (index === null) {
        return null;
      }

      return this.shots[index];
    },

    prevIndex() {
      const index = this.currentIndex;

      if (index === null) {
        return null;
      }

      return index == 0 ? this.shots.length - 1 : index - 1;
    },

    nextIndex() {
      const index = this.currentIndex;

      if (index === null) {
        return null;
      }

      return index + 1 >= this.shots.length ? 0 : index + 1;
    },

    progress() {
      let answered = this.shots.filter(shot => shot.answer !== consts.UNSET)
        .length;
      let total = this.shots.length;
      return parseInt((answered / total) * 100);
    },

    consented() {
      return (
        find(this.shots, shot => get(shot, "answered_at", null) !== null) ||
        this.continueBtnPressed
      );
    }
  },

  created() {
    this.consts = consts;
  },

  mounted() {
    this.fetchShots();

    this.$el.addEventListener("keydown", e => {
      if (this.updating) {
        return;
      }

      switch (e.key) {
        case "ArrowLeft":
          this.prev();
          break;

        case "ArrowRight":
          this.next();
          break;

        default:
          break;
      }
    });
  },
  methods: {
    looksOk() {
      this.updateShot(this.currentShotId, consts.LOOKS_OK);
    },

    looksBad() {
      this.updateShot(this.currentShotId, consts.LOOKS_BAD);
    },

    willDecideLater() {
      this.updateShot(this.currentShotId, "");
    },

    next() {
      if (this.nextIndex !== null) {
        this.currentShotId = this.shots[this.nextIndex].id;
      }
    },

    prev() {
      if (this.prevIndex !== null) {
        this.currentShotId = this.shots[this.prevIndex].id;
      }
    },

    fetchShots() {
      axios
        .all([
          axios.get(printShotFeedbackListUrl(this.config.printId)),
          axios.get(printUrl(this.config.printId))
        ])
        .then(
          axios.spread((printShots, print) => {
            this.shots = printShots.data;
            this.shots.map(item => {
              item.answer =
                item.answer == consts.UNANSWERED ? consts.UNSET : item.answer;
              return item;
            });

            if (this.shots.length > 0) {
              this.currentShotId = this.shots[0].id;
            }
            this.print = print.data;
          })
        )

        .catch(error => {
          console.log(error);
          this.$swal("Ops", "Something went wrong!", "error").then(() =>
            location.reload()
          );
        });
    },

    updateShot: function(id, answer) {
      this.updating = true;
      this.inFlightAnswer = answer;

      axios
        .put(printShotFeedbackUrl(id), { answer: answer })

        .then(response => {
          this.shots = this.shots.map(shot => {
            return shot.id === response.data.id ? response.data : shot;
          });
        })

        .catch(() => {
          this.$swal("Ops", "Could not save answer! Please retry!", "error");
        })

        .finally(() => {
          this.updating = false;
          this.inFlightAnswer = null;
        });
    }
  }
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
