<template>
  <div class="mt-2 mb-5">
    <div class="row justify-content-center">
      <print-card
        v-if="print"
        :print="print"
        @printDeleted="onPrintDeleted"
        @printDataChanged="printDataChanged"
      ></print-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import apis from '../lib/apis'
import { normalizedPrint } from '../lib/normalizers'
import PrintCard from './PrintCard.vue'

export default {
  name: 'PrintPage',

  components: {
    PrintCard
  },

  props: {
    config: Object
  },

  data: function() {
    return {
      print: null
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      axios.get(apis.print(this.config.printId)).then(response => {
        this.print = normalizedPrint(response.data)
      })
    },

    onPrintDeleted() {
      window.location.href = '/prints/'
    },

    printDataChanged() {
      this.fetchData()
    }
  }
}
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass" scoped>
</style>
