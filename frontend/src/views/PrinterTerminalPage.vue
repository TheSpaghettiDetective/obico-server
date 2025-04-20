<template>
  <page-layout>
    <!-- Tob bar -->
    <template #topBarLeft>
      <div class="printer-name truncated">
        {{ printer ? printer.name : '' }}
      </div>
    </template>
    <template #topBarRight>
      <div v-if="printer" class="action-panel">
        <!-- Tunnel -->
        <a
          :href="`/tunnels/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          :title="$t('OctoPrint Tunnel')"
        >
          <svg class="custom-svg-icon">
            <use href="#svg-tunnel" />
          </svg>
          <span class="sr-only">{{ $t("OctoPrint Tunnel") }}</span>
        </a>
        <!-- Configure -->
        <a
          :href="`/printers/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          :title="$t('Configure')"
        >
          <i class="fas fa-wrench"></i>
          <span class="sr-only">{{ $t("Configure") }}</span>
        </a>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="[
              {
                key: 'tunnel',
                svgIcon: 'svg-tunnel',
                title: $t('OctoPrint Tunnel'),
                href: `/tunnels/${printer.id}/`,
              },
              {
                key: 'settings',
                icon: 'fas fa-wrench',
                title: $t('Configure'),
                href: `/printers/${printer.id}/`,
              },
            ]"
            @menuOptionClicked="onMenuOptionClicked"
          />
        </b-dropdown>
      </div>
    </template>
    <!-- Page content -->
    <template #content>
      <div class="contentWrap">
        <printer-terminal
          v-if="printerComm !== null && printer !== null"
          :printer="printer"
          :printer-comm="printerComm"
          :full-screen-height="true"
          :show-full-screen-opt="false"
        ></printer-terminal>
      </div>
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import { printerCommManager } from '@src/lib/printer-comm'
import urls from '@config/server-urls'
import { normalizedPrinter } from '@src/lib/normalizers'
import { user } from '@src/lib/page-context'
import split from 'lodash/split'
import CascadedDropdown from '@src/components/CascadedDropdown'
import PrinterTerminal from '@src/components/terminal/PrinterTerminal'

export default {
  name: 'PrinterTerminalPage',

  components: {
    PageLayout,
    CascadedDropdown,
    PrinterTerminal,
  },

  data: function () {
    return {
      user: null,
      printerId: null,
      printer: null,
      printerComm: null,
    }
  },

  created() {
    this.user = user()
    this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    this.printerComm = printerCommManager.getOrCreatePrinterComm(
      this.printerId,
      urls.printerWebSocket(this.printerId),
      {
        onPrinterUpdateReceived: (data) => {
          this.printer = normalizedPrinter(data, this.printer)
        },
        onTerminalFeedReceived: this.onNextTerminalFeed,
      }
    )
    this.printerComm.connect()
  },

  methods: {
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'share') {
        this.onSharePrinter()
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-name
  font-size: 1rem
  max-width: 360px
  font-weight: bold
  @media (max-width: 768px)
    max-width: 200px

.custom-svg-icon
  height: 1.25rem
  width: 1.25rem
</style>
