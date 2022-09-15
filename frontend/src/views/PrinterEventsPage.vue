<template>
  <layout>
    <template v-slot:content>
      <b-container>
        <b-row class="justify-content-center">
          <div class="col-sm-12 col-md-10 col-lg-8 main-content">
            <printer-event-card v-for="item in printerEvents" :key="item.id" :printer-event="item" />
          </div>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'

import urls from '@config/server-urls'
import Layout from '@src/components/Layout.vue'
import PrinterEventCard from '@src/components/printer-events/PrinterEventCard.vue'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import { normalizedPrinterEvent } from '@src/lib/normalizers'

const LOCAL_PREF_NAMES = {
  filtering: 'printer-events-filtering',
}

const PAGE_SIZE = 12

export default {
  name: 'PrinterEventsPage',

  components: {
    Layout,
    PrinterEventCard,
  },

  props: {
  },

  data() {
    return {
      printerEvents: [],
      loading: false,
      noMoreData: false,
      menuSelections: {
        'Filter By': getLocalPref(
          LOCAL_PREF_NAMES.filtering,
          'none'),
      },
      menuOptions: {
        'Filter By': {
          iconClass: 'fas fa-filter',
          options: [
            {value: 'none', title: 'All'},
            {value: 'errors', title: 'Errors'},
            {value: 'detections', title: 'Failure Alerts'},
            {value: 'print_jobs', title: 'Print Jobs'},
            {value: 'filament_changes', title: 'Filament Changes'},
          ],
        }
      },
    }
  },

  created() {
    this.refetchData()
  },

  methods: {
    fetchMoreData() {
      if (this.noMoreData) {
        return
      }

      this.loading = true
      axios
        .get(urls.printerEvents(), {
          params: {
            start: this.printerEvents.length,
            limit: PAGE_SIZE,
            filter: this.menuSelections['Filter By'],
          }
        })
        .then(response => {
          this.loading = false
          this.noMoreData = response.data.length < PAGE_SIZE
          this.printerEvents.push(...response.data.map(data => normalizedPrinterEvent(data)))
        })
    },
    refetchData() {
      this.printerEvents = []
      this.noMoreData = false
      this.fetchMoreData()
    },
  }
}
</script>

<style lang="sass" scoped>
.main-content
  margin-top: var(--gap-between-blocks)
</style>
