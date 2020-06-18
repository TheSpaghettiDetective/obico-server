<template>
  <div class="col-sm-12 col-md-6 col-lg-4 pt-3">
    <div class="card vld-parent">
      <loading :active="videoDownloading" :is-full-page="true"></loading>
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

        <div class="btn-group btn-group-toggle" data-toggle="buttons">
          <label class="btn" :class="[cardView === 'detective' ? 'btn-primary' : '']">
            <input type="radio" id="detective" value="detective" v-model="cardView" />
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/logo-square-inverted.png')"
            />
          </label>
          <label class="btn" :class="[cardView === 'info' ? 'btn-primary' : '']">
            <input type="radio" id="info" value="info" v-model="cardView" />
            <img
              class="seg-control-icon"
              :src="require('../../../app/static/img/info-inverted.png')"
            />
          </label>
        </div>

        <div class="dropdown">
          <button
            class="btn icon-btn"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-label="Controls"
          >
            <i class="fas fa-ellipsis-v"></i>
          </button>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
            <a class="dropdown-item" v-if="this.print.video_url" @click="downloadVideo(false)">
              <i class="fas fa-download"></i>Download Original Time-lapse
            </a>
            <a
              class="dropdown-item"
              v-if="this.print.tagged_video_url"
              @click="downloadVideo(true)"
            >
              <i class="fas fa-download"></i>Download Detective Time-lapse
            </a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item text-danger" @click="deleteVideo">
              <i class="fas fa-trash-alt"></i>Delete
            </a>
          </div>
        </div>
      </div>
      <div>
        <video-box :videoUrl="print.video_url" />
        <div class="card-body">
          <div class="container">
            <div class="row">
              <div class="text-muted col-4">File:</div>
              <div class="col-8">{{ print.filename }}</div>
            </div>
            <div class="row">
              <div class="text-muted col-4">{{ uploadedTimelapse ? "Uploaded" : "Printed" }}:</div>
              <div
                class="col-8"
              >{{ uploadedTimelapse ? print.uploaded_at.fromNow() : print.ended_at.fromNow() }} {{ endStatus }}</div>
            </div>
            <div class="row" v-if="!uploadedTimelapse">
              <div class="text-muted col-4">Duration:</div>
              <div class="col-8">{{ duration.humanize() }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="false">
        <video-box :videoUrl="print.tagged_video_url" @timeupdate="onTimeUpdate" />
        <gauge :predictionJsonUrl="print.prediction_json_url" :currentPosition="currentPosition" />
        <div class="text-center">
          <div
            class="lead pt-3"
            :class="[print.alerted_at ? 'text-danger' : 'text-success', ]"
          >{{ print.alerted_at ? 'The Detective found spaghetti' : 'The Detective found nothing fishy' }}</div>
        </div>
        <small>Help The Detective get better by giving her feedback.</small>
        <div>
          <div class="custom-control custom-radio">
            <input
              type="radio"
              name="alert_overwrite"
              value="FAILED"
              class="custom-control-input"
              :id="print.id+'_FAILED'"
            />
            <label
              class="custom-control-label"
              :for="print.id+'_FAILED'"
            >Yes, The Detective was right!</label>
          </div>
          <div class="custom-control custom-radio">
            <input
              type="radio"
              name="alert_overwrite"
              value="FAILED"
              class="custom-control-input"
              :id="print.id+'_FAILED'"
            />
            <label
              class="custom-control-label"
              :for="print.id+'_FAILED'"
            >No, The Detective got it wrong!</label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import fileDownload from "js-file-download";
import moment from "moment";
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from "vue-loading-overlay";
import "vue-loading-overlay/dist/vue-loading.css";

import url from "../lib/url";
import VideoBox from "../common/VideoBox";
import Gauge from "../common/Gauge";

export default {
  name: "PrintCard",

  components: {
    Loading,
    VideoBox,
    Gauge
  },

  data: () => {
    return {
      videoDownloading: false,
      currentPosition: 0,
      cardView: "detective"
    };
  },

  props: {
    print: Object
  },

  computed: {
    uploadedTimelapse() {
      return this.print.uploaded_at === null;
    },

    endStatus() {
      return this.print.cancelled_at ? "(Cancelled)" : "";
    },

    duration() {
      return moment.duration(this.print.ended_at.diff(this.print.started_at));
    }
  },

  methods: {
    onTimeUpdate(currentPosition) {
      this.currentPosition = currentPosition;
    },

    downloadVideo(detectiveVideo) {
      this.videoDownloading = true;
      const x = new XMLHttpRequest();
      const filename = `${this.print.filename}${
        detectiveVideo ? "_detective_view" : ""
      }.mp4`;
      x.open(
        "GET",
        detectiveVideo ? this.print.tagged_video_url : this.print.video_url,
        true
      );
      x.responseType = "blob";
      x.onload = e => {
        fileDownload(e.target.response, filename);
        this.videoDownloading = false;
      };
      x.send();
    },

    deleteVideo() {
      axios.get(url.print(this.print.id)).then(() => {
        this.$emit("printDeleted");
      });
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.card-header
  display: flex
  flex-flow: row nowrap
  justify-content: space-between
  align-items: center

.btn-group-toggle
  border-radius: 300px
  .btn
    border: solid thin darken(white, 25)

.seg-control-icon
  height: 1.5rem
</style>
