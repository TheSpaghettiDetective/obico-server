<template>
  <div>
    <div class="row justify-content-center">
      <b-spinner v-if="loading" class="mt-5" label="Loading..."></b-spinner>
      <printer-card
        ref="printer"
        v-if="printer"
        :printer="printer"
        :is-pro-account=true
        :share-token="shareToken"
        @DeleteClicked="onDeleteClicked(printer.id)"
        @NotAFailureClicked="onNotAFailureClicked($event, printer.id, false)"
        @WatchForFailuresToggled="onWatchForFailuresToggled(printer.id)"
        @PauseOnFailureToggled="onPauseOnFailureToggled(printer.id)"
        @PrinterActionPauseClicked="onPrinterActionPauseClicked(printer.id)"
        @PrinterActionResumeClicked="onPrinterActionResumeClicked($event, printer.id)"
        @PrinterActionCancelClicked="onPrinterActionCancelClicked(printer.id)"
        @PrinterActionConnectClicked="onPrinterActionConnectClicked(printer.id)"
        @PrinterActionStartClicked="onPrinterActionStartClicked(printer.id)"
        @PrinterActionControlClicked="onPrinterActionControlClicked(printer.id)"
        @TempEditClicked="onTempEditClicked(printer.id, $event)"
      ></printer-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import split from 'lodash/split'
import Janus from '@lib/janus'

import { normalizedPrinter } from '@lib/normalizers'

import apis from '@lib/apis'
import PrinterWebSocket from '@lib/printer_ws'

import PrinterCard from './PrinterCard.vue'

export default {
  name: 'SharedPrinterPage',
  components: {
    PrinterCard,
  },
  created() {
    this.printerWs = PrinterWebSocket()
    this.webrtc = null
    this.shareToken = split(window.location.pathname, '/').slice(-2, -1).pop()
  },
  data: function() {
    return {
      printer: null,
      shareToken: null,
      videoAvailable: {},
      loading: true,
    }
  },
  methods: {
    fetchPrinter() {
      this.loading = true
      return axios
        .get(apis.pubPrinter(), {
          headers: {
            'Authorization': 'Token ' + this.shareToken
          }
        })
        .then(response => {
          this.loading = false
          this.printer = normalizedPrinter(response.data)
        })
        .catch(() => {
            this.loading = false
        })
    }
  },
  mounted() {
    this.fetchPrinter()

    Janus.init({
      debug: 'all',
      callback: this.onJanusInitalized
    })
  }

}
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@use "~main/theme"

#printer-list-page
  margin-top: 1.5rem

.menu-bar
  background-color: darken(theme.$color-bg-dark, 10)
  padding: 0.75rem
</style>
