<template>
  <div>
    <video-box
      :videoUrl="videoUrl"
      :posterUrl="print.poster_url"
      @timeupdate="onTimeUpdate"
      :fluid="false"
      :autoplay="autoplay"
      :fullScreenBtn="false"
    />
    <gauge :predictionJsonUrl="print.prediction_json_url" :currentPosition="currentPosition" />
  </div>
</template>

<script>
import VideoBox from '../common/VideoBox'
import Gauge from '../common/Gauge'

export default {
  name: 'FullScreenPrintCard',
  components: {
    VideoBox,
    Gauge
  },
  props: {
    print: {
      type: Object,
      required: true
    },
    videoUrl: {
      type: String,
      required: true
    },
    initialPosition: {
      type: Number,
      default: () => 0
    },
    autoplay: {
      type: Boolean,
      default: () => false
    }
  },
  data() {
    return {
      currentPosition: 0
    }
  },
  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition
    },
  }
}
</script>

<style lang="sass" scoped>
</style>
