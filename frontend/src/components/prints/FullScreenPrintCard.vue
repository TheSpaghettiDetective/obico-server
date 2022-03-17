<template>
  <div>
    <video-box
      :videoUrl="videoUrl"
      :posterUrl="print.poster_url"
      @timeupdate="onTimeUpdate"
      :fluid="false"
      :autoplay="autoplay"
      :fullscreenBtn="false"
    />

    <div v-if="isPublic" :style="{opacity: normalizedP > 0.4 ? 1 : 0}" class="bg-warning alert-banner text-center">
      <i class="fas fa-exclamation-triangle"></i> Possible failure detected!
    </div>

    <gauge
      :normalizedP="normalizedP"
    />
  </div>
</template>

<script>
import axios from 'axios'
import {getNormalizedP} from '@src/lib/normalizers'
import VideoBox from '@src/components/VideoBox'
import Gauge from '@src/components/Gauge'

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
    },
    isPublic: {
      type: Boolean,
      default: false
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
      return getNormalizedP(this.predictions, this.currentPosition, this.isPublic)
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
.bg-warning.alert-banner
  position: static
  display: block
  padding: 0.3rem
</style>
