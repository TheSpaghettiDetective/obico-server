<template>
  <div class="card">
    <h5 class="card-header text-center">
      F
      <i class="fas fa-search focused-feedback-icon"></i>CUSED FEEDBACK
    </h5>
    <div class="card-body consent-section">
      <p
        class="text-muted"
      >Help The Detective get better by giving her in-depth feedback on the snapshots of the print.</p>
      <div>
        Number of snapshots:
        <span
          class="feedback-estimate"
        >{{ this.print.printshotfeedback_set.length }}</span>
      </div>
      <p>
        Estimated time to finish:
        <span class="feedback-estimate">{{ this.estimatedFeedbackTime }}</span>
      </p>
      <p>
        You will earn 2 non-expirable Detective Hours after you finish this Focused Feedback.
        <a
          href="https://www.thespaghettidetective.com/docs/how-does-credits-work/"
        >Learn more >>></a>
      </p>
      <button
        v-on:click="$emit('continue-btn-pressed')"
        :disabled="!consentChecked"
        class="btn btn-primary btn-block"
        type="button"
      >Start Focused Feedback</button>
      <br />
      <div class="custom-control custom-checkbox form-check-inline">
        <input
          v-model="consentChecked"
          type="checkbox"
          name="consented"
          class="custom-control-input"
          id="consented-checkbox"
        />
        <label class="custom-control-label" style="font-size: 16px;" for="consented-checkbox">
          I grant The Spaghetti Detective the permission to review the following print's time-lapse video.
          Learn
          <a
            href="#"
          >why this is needed >>></a>
        </label>
      </div>
      <br />
      <div>
        <span class="text-muted">File:</span>
        {{ print.filename }}
      </div>
      <div>
        <span class="text-muted">Printed:</span>
        {{ print.started_at.fromNow() }}
      </div>
      <br />
      <video-box :videoUrl="print.video_url" :posterUrl="print.poster_url" :fullScreenBtn="false" />
    </div>
  </div>
</template>

<script>
import moment from "moment";

import VideoBox from "../../common/VideoBox";

export default {
  name: "Consent",

  props: {
    print: Object
  },

  components: { VideoBox },

  data() {
    return {
      consentChecked: true
    };
  },

  computed: {
    estimatedFeedbackTime() {
      const seconds = this.print.printshotfeedback_set.length * 12;
      if (seconds < 60) {
        return `${seconds} seconds`;
      } else {
        return moment.duration(seconds, "seconds").humanize();
      }
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../../main/main.sass"

.consent-section
  background: $color-bg-dark

.feedback-estimate
  font-size: 1.2em
  font-weight: bolder
  color: $primary
</style>
