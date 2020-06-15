<template>
  <div class="card">
    <div class="card-header">
      <div>
        <span class="text-muted">File:</span>
        {{ print.filename }}
      </div>
      <div>
        <span class="text-muted">Printed:</span>
        {{ print.started_at.fromNow() }}
      </div>
    </div>
    <div class="card-body consent-section">
      <p
        v-if="print.alerted_at !== null"
        class="text-danger lead"
      >Spaghetti detected by The Detective</p>
      <p
        v-if="print.alerted_at === null"
        class="text-success lead"
      >Spaghetti not detected by The Detective</p>
      <p>Did The Detective get it right? If not, help her get better by giving her Focused Feedback and earn some Detective Hours.</p>
      <button
        v-on:click="$emit('continue-btn-pressed')"
        :disabled="!consentChecked"
        class="btn btn-primary btn-block"
        type="button"
      >Give Feedback</button>
      <br />
      <div class="custom-control custom-checkbox form-check-inline">
        <input
          v-model="consentChecked"
          type="checkbox"
          name="consented"
          class="custom-control-input"
          id="consented-checkbox"
        />
        <label
          class="custom-control-label"
          style="font-size: 16px;"
          for="consented-checkbox"
        >I grant The Spaghetti Detective the permission to review this print's time-lapse video.</label>
      </div>
      <video-player
        class="vjs-default-skin vjs-big-play-centered px-4"
        ref="videoPlayer"
        :options="playerOptions"
        :playsinline="true"
      />
    </div>
  </div>
</template>

<script>
import { videoPlayer } from "vue-video-player";
import get from "lodash/get";

export default {
  name: "Entrance",

  props: {
    print: Object
  },

  components: {
    videoPlayer
  },

  data() {
    return {
      consentChecked: true
    };
  },

  computed: {
    playerOptions() {
      return {
        // videojs options
        muted: true,
        language: "en",
        playbackRates: [0.5, 1, 1.5, 2],
        fluid: true,
        sources: [
          {
            type: "video/mp4",
            src: get(this, "print.video_url", null)
          }
        ],
        controlBar: { fullscreenToggle: true },
        poster: get(this, "print.poster_url", null)
      };
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../../main/main.sass"

.consent-section
  background: $color-bg-dark
</style>
