<template>
  <layout>
    <template v-slot:content>
      <b-container>
        <b-row class="justify-content-center">
          <print-card
            v-if="print"
            :print="print"
            @printDeleted="onPrintDeleted"
            @printDataChanged="printDataChanged"
            class="m-0"
          ></print-card>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'

import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import PrintCard from '@src/components/prints/PrintCard.vue'
import Layout from '@src/components/Layout.vue'

export default {
  name: 'PrintPage',

  components: {
    PrintCard,
    Layout,
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
