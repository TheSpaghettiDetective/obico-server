<template>
  <div class="timelapse">
    <div class="my-5 row justify-content-center">
      <div class="col-12">
        <a role="button" class="btn btn-outline-primary btn-block" href="/prints/upload/">
          Upload time-lapses and earn some
          <img
            class="dh-icon"
            :src="require('../../../app/static/img/detective-hour-primary.png')"
          />
        </a>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-12 text-center pb-3">
        <button
          type="button"
          id="delete-prints-btn"
          class="btn btn-light float-right ml-3"
          disabled
        >
          <i class="fas fa-trash-alt"></i> Delete
        </button>
        <button type="button" id="select-all-btn" class="btn btn-primary float-right">Select All</button>
      </div>
    </div>
    <div class="row">
      <print-card v-for="print of displayedPrints" :key="print.id" :print="print"></print-card>
    </div>
    <infinite-loading v-if="prints.length > 0" @infinite="infiniteHandler"></infinite-loading>
  </div>
</template>

<script>
import Vue from "vue";
import axios from "axios";
import filter from "lodash/filter";
import InfiniteLoading from "vue-infinite-loading";

import url from "../lib/url";
import { normalizedPrint } from "../lib/normalizers";
import PrintCard from "./PrintCard.vue";

Vue.use(InfiniteLoading, {
  slots: {
    noMore: "End of your time-apse list."
  }
});

export default {
  name: "PrintsApp",
  components: {
    InfiniteLoading,
    PrintCard
  },
  data: function() {
    return {
      prints: [],
      lastDisplayedIndex: 9
    };
  },

  computed: {
    displayedPrints() {
      return this.prints.slice(0, this.lastDisplayedIndex);
    }
  },

  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get(url.prints()).then(response => {
        this.prints = filter(
          response.data.map(p => normalizedPrint(p)),
          p => p.video_url !== null
        );
      });
    },
    infiniteHandler($state) {
      this.lastDisplayedIndex += 9;
      if (this.lastDisplayedIndex <= this.prints.length) {
        $state.loaded();
      } else {
        $state.complete();
      }
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"
.timelapse
  margin-top: 1.5rem
</style>
