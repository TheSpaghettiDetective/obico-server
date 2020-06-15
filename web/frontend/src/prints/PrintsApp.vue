<template>
  <div class="timelapse">
    <div class="my-5 row justify-content-center">
      <div class="col-12">
        <a role="button" class="btn btn-outline-primary btn-block" href="/prints/upload/">
          Upload time-lapses and earn some
          <img
            class="dh-icon"
            src="{% static 'img/detective-hour-primary.png' %}"
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
      <print-card v-for="print of prints" :key="print.id"></print-card>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import url from "../lib/url";

import PrintCard from "./PrintCard.vue";

export default {
  name: "PrintsApp",
  components: {
    PrintCard
  },
  data: function() {
    return {
      prints: []
    };
  },

  computed: {},

  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get(url.prints()).then(response => {
        this.prints = response.data;
      });
    }
  }
};
</script>

<style lang="sass" scoped>
@import "../main/main.sass"
.timelapse
  margin-top: 1.5rem
</style>
