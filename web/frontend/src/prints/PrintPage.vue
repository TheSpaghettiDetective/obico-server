<template>
  <div class="timelapse">
    <div class="row">
      <print-card v-if="print" :print="print"></print-card>
    </div>
  </div>
</template>

<script>
import axios from "axios";

import apis from "../lib/apis";
import { normalizedPrint } from "../lib/normalizers";
import PrintCard from "./PrintCard.vue";

export default {
  name: "PrintPage",

  components: {
    PrintCard
  },

  props: {
    config: Object
  },

  data: function() {
    return {
      print: null
    };
  },

  mounted() {
    this.fetchData();
  },

  methods: {
    fetchData() {
      axios.get(apis.print(this.config.printId)).then(response => {
        this.print = normalizedPrint(response.data);
      });
    }
  }
};
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@use "~main/theme"

.timelapse
  margin-top: 1.5rem
</style>
