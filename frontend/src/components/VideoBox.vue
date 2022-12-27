<template>
  <div class="card-img-top">
    <video-player
      class="vjs-default-skin vjs-big-play-centered"
      ref="videoPlayer"
      :options="playerOptions"
      :playsinline="true"
      @timeupdate="onTimeUpdate"
    />
    <div class="buttons-container">
      <a v-if="downloadBtn" class="download-btn" role="button" @click="$emit('download')" title="Download">
        <i class="fas fa-download" aria-hidden="true"></i>
      </a>
      <a v-if="fullscreenBtn" class="fullscreen-btn" role="button" @click="$emit('fullscreen')" title="Full screen">
        <i class="fa fa-expand" aria-hidden="true"></i>
      </a>
    </div>
  </div>
</template>

<script>
import 'video.js/dist/video-js.css'
import { videoPlayer } from 'vue-video-player'

export default {
  name: 'VideoBox',
  components: {
    videoPlayer
  },
  props: {
    videoUrl: String,
    posterUrl: String,
    fullscreenBtn: {
      type: Boolean,
      default: true,
    },
    downloadBtn: {
      type: Boolean,
      default: false,
    },
    fluid: {
      type: Boolean,
      default: true,
    },
    autoplay: {
      type: Boolean,
      default: false,
    },
    defaultFullScreenToggle: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    playerOptions() {
      return {
        // videojs options
        muted: true,
        preload: 'none',
        language: 'en',
        playbackRates: [0.5, 1, 1.5, 2],
        fluid: this.fluid,
        fill: !this.fluid,
        autoplay: this.autoplay,
        sources: [
          {
            type: 'video/mp4',
            src: this.videoUrl
          }
        ],
        controlBar: { fullscreenToggle: this.defaultFullScreenToggle },
        poster: this.posterUrl,
      }
    }
  },
  methods: {
    onTimeUpdate(event) {
      this.$emit('timeupdate', event.currentTime() / event.duration())
    }
  }
}
</script>

<style lang="sass" scoped>
.card-img-top
  position: relative
  background-color: black

  .buttons-container
    position: absolute
    top: 0
    right: 0
    padding: 0.5rem
    background-color: rgba(0,0,0,0.7)

  a.fullscreen-btn, a.download-btn
    padding: 0.5rem
    color: rgba(255,255,255,0.5)
    font-size: 1.5rem
    transition: all .3s ease-out
    &:hover
      color: rgba(255,255,255,0.9)
</style>
