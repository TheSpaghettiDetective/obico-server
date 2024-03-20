<template>
  <div>
    <video-box
      :video-url="videoUrl"
      :poster-url="print.poster_url"
      :fluid="false"
      :autoplay="autoplay"
      :fullscreen-btn="false"
      @timeupdate="onTimeUpdate"
    />

    <div
      v-if="isPublic"
      :style="{ opacity: normalizedP > 0.4 ? 1 : 0 }"
      class="bg-warning alert-banner text-center"
    >
      <i class="fas fa-exclamation-triangle"></i> {{$t("Possible failure detected!")}}
    </div>

    <failure-detection-gauge :normalized-p="normalizedP" />
  </div>
</template>

<script>
import axios from 'axios'
import { getNormalizedP } from '@src/lib/utils'
import VideoBox from '@src/components/VideoBox'
import FailureDetectionGauge from '@src/components/FailureDetectionGauge'

export default {
  name: 'FullScreenPrintCard',
  components: {
    VideoBox,
    FailureDetectionGauge,
  },
  props: {
    print: {
      type: Object,
      required: true,
    },
    videoUrl: {
      type: String,
      required: true,
    },
    initialPosition: {
      type: Number,
      default: () => 0,
    },
    autoplay: {
      type: Boolean,
      default: () => false,
    },
    isPublic: {
      type: Boolean,
      default: false,
    },
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
    },
  },
  mounted() {
    if (this.print.prediction_json_url) {
      this.fetchPredictions()
    }
  },
  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition
    },

    fetchPredictions() {
      axios.get(this.print.prediction_json_url).then((response) => {
        this.predictions = response.data
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.bg-warning.alert-banner
  position: static
  display: block
  padding: 0.3rem
</style>
