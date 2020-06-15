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
      <div class="card-img-top">
        <video-player
          class="vjs-default-skin vjs-big-play-centered px-4"
          ref="videoPlayer"
          :options="playerOptions"
          :playsinline="true"
        />
        <a class="fullscreen-btn" href="#tl-fullscreen-modal" role="button" data-toggle="modal">
          <i class="fa fa-expand fa-2x" aria-hidden="true"></i>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { videoPlayer } from "vue-video-player";
import get from "lodash/get";

export default {
  name: "PrintCard",
  components: {
    videoPlayer
  },
  props: {
    print: Object
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
