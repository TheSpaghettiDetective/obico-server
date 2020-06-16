<template>
  <div class="col-sm-12 col-md-6 col-lg-4 timelapse-card">
    <div class="card">
      <div class="card-header">
        <div
          class="custom-control custom-checkbox form-check-inline float-left"
          style="padding-top: 2px;"
        >
          <input
            type="checkbox"
            name="selected_print_ids"
            class="custom-control-input"
            form="prints-form"
          />
          <label class="custom-control-label"></label>
        </div>
        <a
          role="button"
          class="btn btn-outline-danger float-right btn-sm borderless"
          data-toggle="tooltip"
          data-placement="top"
          title="Delete"
        >
          <i class="fas fa-trash-alt fa-lg"></i>
        </a>
        <div class="dropdown float-right">
          <a
            role="button"
            class="btn btn-sm borderless dropdown-toggle"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
          >
            <i class="fas fa-download"></i>
          </a>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
            <a
              class="download dropdown-item"
              data-mime-type="video/mp4"
            >Download Original Time-lapse</a>
            <a class="download dropdown-item" data-mime-type="video/mp4">Download Detective View</a>
          </div>
        </div>
      </div>
      <video-box :videoUrl="print.tagged_video_url" @timeupdate="onTimeUpdate" />
      <gauge :predictionJsonUrl="print.prediction_json_url" :currentPosition="currentPosition" />
      <div class="text-center">
        <div
          class="lead"
          :class="[print.alerted_at ? 'text-danger' : 'text-success', ]"
        >{{ print.alerted_at ? 'Spaghetti was detected on this print' : 'The Detective thought it was successful' }}</div>
        <div>
          <radio-group :options="['She was right!', 'She got it wrong!']" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VideoBox from "../common/VideoBox";
import Gauge from "../common/Gauge";
import RadioGroup from "../common/RadioGroup";

export default {
  name: "PrintCard",
  components: {
    VideoBox,
    Gauge,
    RadioGroup
  },
  data: () => {
    return {
      currentPosition: 0
    };
  },
  props: {
    print: Object
  },
  computed: {},
  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition;
    }
  }
};
</script>

<style></style>
