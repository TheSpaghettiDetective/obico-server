<template>
  <card>
    <div class="card-header">Focused Feedback</div>
    <div>
      <button
        v-on:click="$emit('continue-btn-pressed')"
        class="btn btn-primary btn-block"
        type="button"
      >Give Feedback</button>
      <div>By pressing the "Give Focused Feedback" button below, you grant The Spaghetti Detective the permission to review the time-lapse video shown above.</div>
      <video-player
        class="vjs-default-skin vjs-big-play-centered"
        ref="videoPlayer"
        :options="playerOptions"
        :playsinline="true"
      />
    </div>
  </card>
</template>

<script>
import { videoPlayer } from "vue-video-player";
import get from "lodash/get";
import Card from "../../common/Card.vue";

export default {
  name: "Entrance",

  props: {
    print: Object
  },

  components: {
    videoPlayer,
    Card
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

<style></style>
