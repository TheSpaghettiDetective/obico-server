<template>
  <widget-template>
    <template #title>{{ $t("Printer Terminal") }}</template>
    <template #content>
      <div class="terminal-widget">
        <printer-terminal
          :printer="printer"
          :printer-comm="printerComm"
          :show-full-screen-opt="true"
        ></printer-terminal>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import PrinterTerminal from '@src/components/terminal/PrinterTerminal'

export default {
  name: 'TerminalWidget',

  components: {
    WidgetTemplate,
    PrinterTerminal,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
    printerComm: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="sass" scoped>
.terminal-widget
  height: 400px
  display: flex
</style>
