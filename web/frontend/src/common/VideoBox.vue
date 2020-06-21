<template>
  <div class="card-img-top">
    <video-player
      class="vjs-default-skin vjs-big-play-centered"
      ref="videoPlayer"
      :options="playerOptions"
      :playsinline="true"
      @timeupdate="onTimeUpdate"
    />
    <a class="fullscreen-btn" href="#tl-fullscreen-modal" role="button" data-toggle="modal">
      <i class="fa fa-expand fa-2x" aria-hidden="true"></i>
    </a>
  </div>
</template>

<script>
import { videoPlayer } from "vue-video-player";

export default {
  name: "VideoBox",
  components: {
    videoPlayer
  },
  props: {
    videoUrl: String,
    posterUrl: String
  },
  computed: {
    playerOptions() {
      return {
        // videojs options
        muted: true,
        preload: "none",
        language: "en",
        playbackRates: [0.5, 1, 1.5, 2],
        fluid: true,
        sources: [
          {
            type: "video/mp4",
            src: this.videoUrl
          }
        ],
        controlBar: { fullscreenToggle: false },
        poster: this.posterUrl
      };
    }
  },
  methods: {
    onTimeUpdate(event) {
      this.$emit("timeupdate", event.currentTime() / event.duration());
    }
  }
};
</script>

<style lang="sass" scoped>
.card-img-top
  position: relative
  background-color: black

  a.fullscreen-btn
    position: absolute
    top: 0
    right: 0
    padding: 0.5rem
    background-color: rgba(0,0,0,0.7)
    color: rgba(255,255,255,0.5)
</style>
