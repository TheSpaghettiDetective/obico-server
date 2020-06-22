<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <content-placeholders v-if="print === null">
        <content-placeholders-img />
        <content-placeholders-img />
        <content-placeholders-text :lines="5" />
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
        </div>
        <div class="progress-info p-3">
          <div class="clearfix">
            <div class="float-left">
              #{{ currentIndex + 1 }} of
              <strong>{{ this.shots.length }}</strong> pictures
            </div>
            <div class="float-right">
              <strong v-if="progress == 100">All answered!</strong>
              <strong v-if="progress != 100">{{ progress }}% answered</strong>
            </div>
          </div>
          <progress-bar class="clearfix" :max="100" :value="progress">{{ progress }} %</progress-bar>
          <a
            v-if="progress == 100"
            type="button"
            class="btn btn-success btn-block my-3"
            href="/prints/"
          >Done</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";
import AnswerButton from "./components/AnswerButton.vue";
import ProgressBar from "./components/ProgressBar.vue";
import Consent from "./components/Consent";
import url from "../lib/url";
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
      axios;
      // .all([
      //   axios.get(url.printShotFeedbackList(this.config.printId)),
      axios
        .get(url.print(this.config.printId))
        // ])
        .then(
          // axios.spread((printShots, print) => {
          //   this.shots = printShots.data;
          //   if (this.shots.length > 0) {
          //     this.currentShotId = this.shots[0].id;
          //   }
          response => {
            this.print = normalizedPrint(response.data);
            this.shots = this.print.printshotfeedback_set;
            if (this.shots.length > 0) {
              this.currentShotId = this.shots[0].id;
            }
          }
        );
      // );
    },

    updateShot: function(id, answer) {
      this.updating = true;
      this.inFlightAnswer = answer;

      axios
        .put(url.printShotFeedback(id, this.print.id), { answer: answer })

        .then(response => {
          const { instance, credited_dhs } = response.data;
          this.shots = this.shots.map(shot => {
            return shot.id === instance.id ? instance : shot;
          });
          if (credited_dhs >= 0) {
            this.$swal({
              text:
                "You just earned 2 Detective Hours by completeing the Focused Feedback for The Detective! Thank you!",
              toast: true,
              position: "top-end",
              showConfirmButton: false,
              timer: 5000
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
        .patch(url.print(this.print.id), data)

        .then(response => (this.print = response.data));
    },

    consentBtnPressed: function() {
      this.updatePrint({ access_consented_at: moment() });
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.printshots-container
  margin-top: 1.5em

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
  background: $color-bg-dark
</style>
