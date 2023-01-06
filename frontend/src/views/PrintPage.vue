<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row class="justify-content-center">
          <print-card
            v-if="print"
            :print="print"
            class="m-0"
            @printDeleted="onPrintDeleted"
            @printDataChanged="printDataChanged"
          ></print-card>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'

import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import PrintCard from '@src/components/prints/PrintCard.vue'
import PageLayout from '@src/components/PageLayout.vue'

export default {
  name: 'PrintPage',

  components: {
    PrintCard,
    PageLayout,
  },

  props: {
    config: Object,
  },

  data: function () {
    return {
      print: null,
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      axios.get(urls.print(this.config.printId)).then((response) => {
        this.print = normalizedPrint(response.data)
      })
    },

    onPrintDeleted() {
      window.location.href = '/prints/'
    },

    printDataChanged() {
      this.fetchData()
    },
  },
}
</script>

<style lang="sass" scoped></style>
