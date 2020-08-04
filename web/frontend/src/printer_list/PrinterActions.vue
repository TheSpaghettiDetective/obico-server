<template>
<div>
  <div class="row my-2">
    <div
      v-if="status && error"
      class="col-12 bg-danger text-center">
      <div>OctoPrint Error</div><div>{{ printerStateTxt }}</div>
    </div>

    <div
      v-if="status && !disconnected && !idle"
      class="col-sm-6"
    >
      <button
        id="print-pause-resume"
        type="button"
        class="btn btn-block mt-2"
        :class="{'btn-outline-warning': !printerPaused, 'btn-outline-success': printerPaused}"
        @click="onPauseToggled($event)"
      >
        <span
          v-if="!printerPaused"
        >
          <i class="fas fa-pause"></i>&nbsp;&nbsp;Pause
        </span>

        <span
          v-if="printerPaused"
        >
          <i class="fas fa-play"></i>&nbsp;&nbsp;Resume
        </span>
      </button>
    </div>

    <div
      v-if="status && !disconnected && !idle"
      class="col-sm-6"
    >
      <button
        id="print-cancel"
        type="button"
        class="btn btn-outline-danger btn-block mt-2 mb-2"
        @click="$emit('PrinterActionCancelClicked', $event)"
      >
        <i class="fas fa-stop"></i>&nbsp;&nbsp;Cancel
      </button>
    </div>


    <div
      v-if="status && !disconnected && idle"
      class="col-sm-6"
    >
      <button
        id="start-print"
        type="button"
        class="btn btn-outline-primary btn-block mt-2"
        @click="$emit('PrinterActionStartClicked', $event)"
      >
        <i class="fas fa-star"></i>&nbsp;&nbsp;Start Printing
      </button>
    </div>

    <div
      v-if="status && !disconnected && idle"
      class="col-sm-6"
    >
      <a
        type="button"
        role="button"
        class="btn btn-outline-secondary btn-block mt-2 mb-2"
        @click="$emit('PrinterActionControlClicked', $event)"
      >
        <i class="fas fa-arrows-alt"></i>&nbsp;&nbsp;Control
      </a>
    </div>

    <div
      v-if="status && disconnected"
      class="col-12 text-center py-2 text-warning"
    >
      <div>Printer is not connected to OctoPrint.</div>
      <button
        id="connect-printer"
        type="button"
        class="btn btn-outline-primary btn-block mt-2"
        @click="$emit('PrinterActionConnectClicked', $event)"
        :disabled="connecting"
      >
        <i class="fab fa-usb"></i>&nbsp;&nbsp;Connect
        <i
          v-if="connecting"
          class="fas fa-spinner fa-spin"
        ></i>
      </button>
    </div>

    <div
      v-if="!status"
      class="col-12 text-center py-3 text-warning"
    >
      <div>
        OctoPrint is not powered on, or is offline.
        <a href="https://www.thespaghettidetective.com/docs/octoprint-is-offline/">Why?</a>
      </div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  name: 'PrinterActions',
  props: {
    printerId: {},
    status: {},
    printerStateTxt: {},
    printerPaused: {},
    idle: {},
    error: {},
    disconnected: {},

    // --

    connecting: {},
  },
  computed: {
  },
  methods: {
    onPauseToggled(ev) {
      if (this.printerPaused) {
        this.$emit('PrinterActionResumeClicked', ev)
      } else {
        this.$emit('PrinterActionPauseClicked', ev)
      }
    },
  }
}
</script>
