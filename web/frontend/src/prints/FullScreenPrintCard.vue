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
    <gauge
      :normalizedP="normalizedP"
    />
  </div>
</template>

<script>
import axios from 'axios'
import {getNormalizedP} from '@lib/normalizers'
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
      currentPosition: 0,
      predictions: [],
    }
  },
  computed: {
    normalizedP() {
      return getNormalizedP(this.predictions, this.currentPosition)
    }
  },
  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition
    },

    fetchPredictions() {
      axios.get(this.print.prediction_json_url).then(response => {
        this.predictions = response.data
      })
    }
  },
  mounted() {
    if (this.print.prediction_json_url) {
      this.fetchPredictions()
    }
  },
}
</script>

<style lang="sass" scoped>
</style>
