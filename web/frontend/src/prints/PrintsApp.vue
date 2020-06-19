<template>
  <div class="timelapse" sticky-container>
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
    <div v-sticky sticky-offset="{top: 0, bottom: 30}" sticky-side="both" on-stick="onMenuStick">
      <b-dropdown toggle-class="text-decoration-none" no-caret>
        <template v-slot:button-content>
          <i class="fas fa-filter"></i>
        </template>
        <b-dropdown-item @click="onFilterClick('none')">
          <i class="fas fa-check" :style="{visibility: filter === 'none' ? 'visible' : 'hidden'}"></i>All
        </b-dropdown-item>
        <b-dropdown-divider></b-dropdown-divider>
        <b-dropdown-item @click="onFilterClick('finished')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'finished' ? 'visible' : 'hidden'}"
          ></i>Finished prints
        </b-dropdown-item>
        <b-dropdown-item @click="onFilterClick('cancelled')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'cancelled' ? 'visible' : 'hidden'}"
          ></i>Cancelled prints
        </b-dropdown-item>
        <b-dropdown-item @click="onFilterClick('pendingReview')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'pendingReview' ? 'visible' : 'hidden'}"
          ></i>Prints pending review
        </b-dropdown-item>
      </b-dropdown>
    </div>
    <div class="row">
      <print-card
        v-for="print of displayedPrints"
        :key="print.id"
        :print="print"
        @selectedChange="onSelectedChange"
      ></print-card>
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
    noMore: "End of your time-lapse list."
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
      selectedPrintIds: new Set(),
      lastDisplayedIndex: 9,
      filter: "none"
    };
  },

  computed: {
    displayedPrints() {
      return filter(this.prints, p => {
        return !this.cancelledPrintsOnly || p.is_cancelled;
      }).slice(0, this.lastDisplayedIndex);
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
    },

    onSelectedChange(printId, selected) {
      if (selected) {
        this.selectedPrintIds.add(printId);
      } else {
        this.selectedPrintIds.delete(printId);
      }
    },

    onMenuStick(data) {
      console.log(data);
    },

    onFilterClick(filter) {
      this.filter = filter;
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"

.timelapse
  margin-top: 1.5rem
</style>
