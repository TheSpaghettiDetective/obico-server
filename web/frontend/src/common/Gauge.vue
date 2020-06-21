<template>
  <div class="tsd-gauge-container">
    <div class="tsd-gauge">
      <radial-gauge :value="value" :title="title" :options="options"></radial-gauge>
    </div>
    <hr />
  </div>
</template>

<script>
import axios from "axios";
import get from "lodash/get";
import RadialGauge from "vue2-canvas-gauges/src/RadialGauge";

const ALERT_THRESHOLD = 0.4;

export default {
  components: {
    RadialGauge
  },
  data: () => {
    return {
      predictions: [],
      currentValue: 0
    };
  },
  props: {
    title: {
      type: String,
      default: "Looking Good"
    },

    currentPosition: {
      type: Number,
      default: 0
    },

    predictionJsonUrl: String,

    options: {
      // https://canvas-gauges.com/documentation/user-guide/configuration
      type: Object,
      default: () => ({
        valueDec: 0,
        valueInt: 0,
        width: 240,
        height: 240,
        units: false,
        box: false,
        minValue: 0,
        maxValue: 100,
        majorTicks: ["", "", "", ""],
        minorTicks: 4,
        highlights: [
          { from: 0, to: 33, color: "#5cb85c" },
          { from: 33, to: 67, color: "#f0ad4e" },
          { from: 67, to: 100, color: "#d9534f" }
        ],
        colorPlate: "rgba(255,255,255,.0)",
        colorTitle: "#5cb85c",
        colorStrokeTicks: "#EBEBEB",
        colorNeedleStart: "rgba(240, 128, 128, 1)",
        colorNneedleEnd: "rgba(255, 160, 122, .9)",
        valueBox: false,
        animationRule: "bounce",
        animationDuration: 500,
        animatedValue: true,
        startAngle: 90,
        ticksAngle: 180,
        borders: false
      })
    }
  },

  computed: {
    value() {
      const num = Math.round(this.predictions.length * this.currentPosition);
      return this.scaleP(get(this.predictions[num], "fields.ewm_mean"));
    }
  },

  mounted() {
    this.fetchData();
  },

  methods: {
    fetchData() {
      axios.get(this.predictionJsonUrl).then(response => {
        this.predictions = response.data;
      });
    },

    scaleP(p) {
      var scaleAboveCutOff = 100.0 / 3.0 / (1 - ALERT_THRESHOLD);
      var scaleBelowCutOff = 200.0 / 3.0 / ALERT_THRESHOLD;
      if (p > ALERT_THRESHOLD) {
        return (p - ALERT_THRESHOLD) * scaleAboveCutOff + 200.0 / 3.0;
      } else {
        return p * scaleBelowCutOff;
      }
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.tsd-gauge-container
  padding: 0 16px
  .tsd-gauge
    text-align: center
    padding: 8px
    margin-bottom: -150px
  hr
    background-color: #EBEBEB
    height: 1px
    margin-top: 15px
</style>
