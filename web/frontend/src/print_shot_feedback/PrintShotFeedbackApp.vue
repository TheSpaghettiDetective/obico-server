<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <div class="card">
        <h5 class="card-header text-center">
          F
          <i class="fas fa-search focused-feedback-icon"></i>CUSED FEEDBACK
        </h5>
        <progress-bar :max="100" :value="progress">{{ progress }} %</progress-bar>
        <content-placeholders v-if="print === null">
          <content-placeholders-text :lines="2" />
          <content-placeholders-text :lines="5" />
          <content-placeholders-img />
        </content-placeholders>

        <consent
          v-if="print !== null && !print.access_consented_at"
          :print="this.print"
          @continue-btn-pressed="this.consentBtnPressed"
        />
        <div class="card" v-if="print !== null && currentShot && print.access_consented_at">
          <div class="current-shot-container">
            <img class="card-img-top" @click="next" :src="currentShot.image_url" />
            <button
              v-if="currentIndex !== prevIndex"
              class="prev-btn btn btn-primary"
              :disabled="updating"
              @click="prev"
            >
              <i class="fas fa-lg fa-angle-left" />
            </button>
            <button
              v-if="currentIndex !== nextIndex"
              class="next-btn btn btn-primary"
              :disabled="updating"
              @click="next"
            >
              <i class="fas fa-lg fa-angle-right" />
            </button>
          </div>
          <div class="card-body progress-info">
            <div class="text-center">
              <answer-button
                ref="button"
                :checked="currentShot.answer === consts.LOOKS_BAD"
                :updating="inFlightAnswer === consts.LOOKS_BAD && updating"
                :disabled="updating"
                checked-class="btn-primary"
                @click="looksBad"
              >Yes, I do see spaghetti</answer-button>
              <answer-button
                :checked="currentShot.answer === consts.LOOKS_OK"
                :updating="inFlightAnswer === consts.LOOKS_OK && updating"
                :disabled="updating"
                checked-class="btn-primary"
                @click="looksOk"
              >No, I don't see spaghetti</answer-button>
              <answer-button
                :checked="currentShot.answer === consts.UNANSWERED"
                :updating="inFlightAnswer === consts.UNANSWERED && updating"
                :disabled="updating"
                checked-class="btn-primary"
                @click="willDecideLater"
              >Hmmm, I am not sure</answer-button>
            </div>
            <small class="float-right text-muted">
              Not sure? Look at
              <a href="#">some examples >>></a>
            </small>
          </div>
          <div class="card-body p-3">
            <a href="/prints/">
              <i class="fas fa-chevron-left"></i> Time-lapse
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";
import sortBy from "lodash/sortBy";

import AnswerButton from "./components/AnswerButton.vue";
import ProgressBar from "./components/ProgressBar.vue";
import Consent from "./components/Consent";
import apis from "../lib/apis";
import { normalizedPrint } from "../lib/normalizers";

const consts = {
  LOOKS_OK: "LOOKS_OK",
  LOOKS_BAD: "LOOKS_BAD",
  UNANSWERED: "UNDECIDED",
  UNSET: null
};

export default {
  name: "PrintShotFeedbackApp",
  components: {
    AnswerButton,
    ProgressBar,
    Consent
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
      updating: false,
      inFlightAnswer: null,
      shots: [],
      print: null
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

      return index == 0 ? 0 : index - 1;
    },

    nextIndex() {
      const index = this.currentIndex;

      if (index === null) {
        return null;
      }

      return index + 1 >= this.shots.length ? this.shots.length - 1 : index + 1;
    },

    progress() {
      let total = this.shots.length;
      return parseInt((this.currentIndex / total) * 100)+1;
    }
  },

  created() {
    this.consts = consts;
  },

  mounted() {
    this.fetchData();

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
      this.updateShot(this.currentShotId, consts.UNANSWERED);
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

    fetchData() {
      axios.get(apis.print(this.config.printId)).then(response => {
        this.print = normalizedPrint(response.data);
        this.shots = sortBy(this.print.printshotfeedback_set, "id");
        if (this.shots.length > 0) {
          this.currentShotId = this.shots[0].id;
        }
      });
    },

    updateShot: function(id, answer) {
      this.updating = true;
      this.inFlightAnswer = answer;

      axios
        .put(apis.printShotFeedback(id, this.print.id), { answer: answer })

        .then(response => {
          const { instance, credited_dhs } = response.data;
          this.shots = this.shots.map(shot => {
            return shot.id === instance.id ? instance : shot;
          });
          if (credited_dhs > 0) {
            this.$swal({
              title: "Thank you!",
              html:
                "<p>The Detective just got a little smarter because of your feedback!</p><p>And you just earned 2 non-expirable Detective Hours - Yay!</p>",
              confirmButtonText: "I'm done!",
              showCancelButton: true,
              cancelButtonText: "Change feedback"
            }).then(result => {
              if (result.isConfirmed) {
                window.location.href = "/prints/";
              }
            });
          }
        })

        .finally(() => {
          this.updating = false;
          this.inFlightAnswer = null;
          this.next();
        });
    },

    updatePrint: function(data) {
      axios
        .patch(apis.print(this.print.id), data)

        .then(response => (this.print = response.data));
    },

    consentBtnPressed: function() {
      this.updatePrint({ access_consented_at: moment() });
    }
  }
};
</script>

<style lang="sass" scoped>
@use "~main/theme"

.printshots-container
  margin-top: 0.5rem

.current-shot-container
  position: relative

.prev-btn
  display: inline
  position: absolute
  left: 2%
  top: 40%
  opacity: 0.5

.next-btn
  display: inline
  position: absolute
  right: 2%
  top: 40%
  opacity: 0.5

.progress-info
  background: theme.$color-bg-dark
</style>
