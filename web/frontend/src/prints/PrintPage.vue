<template>
  <div class="mt-2 mb-5">
    <pull-to-reveal>
      <navbar view-name="app.views.web_views.print"></navbar>
    </pull-to-reveal>

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

import urls from '../lib/server_urls'
import { normalizedPrint } from '../lib/normalizers'
import PrintCard from './PrintCard.vue'
import PullToReveal from '@common/PullToReveal.vue'
import Navbar from '@common/Navbar.vue'

export default {
  name: 'PrintPage',

  components: {
    PrintCard,
    PullToReveal,
    Navbar,
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
      axios.get(urls.print(this.config.printId)).then(response => {
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
