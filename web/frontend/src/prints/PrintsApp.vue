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
    <div
      class="menu-bar text-right"
      v-sticky
      sticky-offset="{top: 0, bottom: 30}"
      sticky-side="both"
      on-stick="onMenuStick"
    >
      <b-dropdown
        toggle-class="text-decoration-none btn-sm square-btn"
        :variant="filterBtnVariant"
        no-caret
      >
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
          ></i>Finished
        </b-dropdown-item>
        <b-dropdown-item @click="onFilterClick('cancelled')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'cancelled' ? 'visible' : 'hidden'}"
          ></i>Cancelled
        </b-dropdown-item>
        <b-dropdown-item @click="onFilterClick('pendingReview')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'pendingReview' ? 'visible' : 'hidden'}"
          ></i>Review needed
        </b-dropdown-item>
        <b-dropdown-item @click="onFilterClick('pendingFocusedReview')">
          <i
            class="fas fa-check"
            :style="{visibility: filter === 'pendingFocusedReview' ? 'visible' : 'hidden'}"
          ></i>Focused-review needed
        </b-dropdown-item>
      </b-dropdown>
      <button
        type="button"
        class="btn ml-3"
        :class="{'btn-light': !anyPrintsSelected, 'btn-danger': anyPrintsSelected}"
        :disabled="!anyPrintsSelected"
        @click="onDeleteBtnClick"
      >
        <i class="fas fa-trash-alt"></i>
        Delete {{ anyPrintsSelected ? ' (' + selectedPrintIds.size + ')' : '' }}
      </button>
    </div>
    <div class="row">
      <print-card
        v-for="print of visiblePrints"
        :key="print.id"
        :print="print"
        @selectedChange="onSelectedChange"
        @printDeleted="fetchData"
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
      lastDisplayedIndex: 12,
      filter: "none"
    };
  },

  computed: {
    visiblePrints() {
      return filter(this.prints, p => {
        if (this.filter === "cancelled") {
          return p.is_cancelled;
        } else if (this.filter === "finished") {
          return p.is_finished;
        } else if (this.filter === "pendingReview") {
          return p.has_detective_view && p.alert_overwrite === null;
        } else if (this.filter === "pendingFocusedReview") {
          return p.focused_review_pending;
        } else {
          return true;
        }
      }).slice(0, this.lastDisplayedIndex);
    },

    filterBtnVariant() {
      return this.filter === "none" ? "outline-secondary" : "outline-primary";
    },

    anyPrintsSelected() {
      return this.selectedPrintIds.size > 0;
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
        this.selectedPrintIds = new Set();
      });
    },

    infiniteHandler($state) {
      this.lastDisplayedIndex += 12;
      if (this.lastDisplayedIndex <= this.visiblePrints.length) {
        $state.loaded();
      } else {
        $state.complete();
      }
    },

    onSelectedChange(printId, selected) {
      const selectedPrintIdsClone = new Set(this.selectedPrintIds);
      if (selected) {
        selectedPrintIdsClone.add(printId);
      } else {
        selectedPrintIdsClone.delete(printId);
      }
      this.selectedPrintIds = selectedPrintIdsClone;
    },

    onMenuStick(data) {
      console.log(data);
    },

    onFilterClick(filter) {
      this.filter = filter;
    },

    onDeleteBtnClick() {
      const selectedPrintIds = this.selectedPrintIds;
      this.$swal({
        title: "Are you sure?",
        text: `Delete ${this.selectedPrintIds.size} print(s)? This action can not be undone.`,
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No"
      }).then(userAction => {
        if (userAction.isConfirmed) {
          axios
            .post(url.printsBulkDelete(), { print_ids: selectedPrintIds })
            .then(() => {
              this.fetchData();
            });
        }
      });
    }
  }
};
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@import "../main/main.sass"

.timelapse
  margin-top: 1.5rem

.menu-bar
  background-color: darken($color-bg-dark, 10)
  padding: 0.75rem
</style>
