<template>
  <widget-template>
    <template #title>Printer Terminal</template>
    <template #content>
      <printer-terminal :printer="printer" :printer-comm="printerComm"></printer-terminal>
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

<style lang="sass" scoped></style>
