<template>
<div>
  <div class="row my-2" v-if="!printer.isOffline() && printer.hasError()">
    <div class="col-12 bg-danger text-center">
      <div>OctoPrint Error</div><div>{{ printer.status.state.text }}</div>
    </div>
  </div>
  <div class="row my-2" v-if="printer.inUserInteractionRequired()">
    <div class="col-12 bg-warning text-center">
      <div>Filament change or user interaction required</div>
    </div>
  </div>
  <div class="row my-2" v-if="printer.inTransientState()">
    <div class="col-12 text-center my-3">
      <b-spinner label="Processing..."></b-spinner>
      <div>{{ printer.status.state.text }} ...</div>
    </div>
  </div>
  <div class="row my-2" v-else>
    <div
      v-if="!printer.isOffline() && !printer.isDisconnected() && !printer.isIdle()"
      class="col-sm-6"
    >
      <button
        v-if="!printer.isPaused()"
        type="button"
        class="btn btn-block mt-2 btn-outline-warning"
        @click="onPauseToggled($event)"
      >
        <i class="fas fa-pause"></i>&nbsp;Pause
      </button>
      <button
        v-else
        type="button"
        class="btn btn-block mt-2 btn-outline-success"
        @click="onPauseToggled($event)"
      >
        <i class="fas fa-play"></i>&nbsp;Resume
      </button>
    </div>

    <div
      v-if="!printer.isOffline() && !printer.isDisconnected() && !printer.isIdle()"
      class="col-sm-6"
    >
      <button
        id="print-cancel"
        type="button"
        class="btn btn-outline-danger btn-block mt-2 mb-2"
        @click="$emit('PrinterActionCancelClicked', $event)"
      >
        <i class="fas fa-stop"></i>&nbsp;Cancel
      </button>
    </div>


    <div
      v-if="!printer.isOffline() && !printer.isDisconnected() && printer.isIdle()"
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
      v-if="!printer.isOffline() && !printer.isDisconnected() && printer.isIdle()"
      class="col-sm-6"
    >
      <button
        type="button"
        class="btn btn-outline-secondary btn-block mt-2 mb-2"
        @click="$emit('PrinterActionControlClicked', $event)"
      >
        <i class="fas fa-arrows-alt"></i>&nbsp;&nbsp;Control
      </button>
    </div>
  </div>
  <div class="row my-2" v-if="!printer.isOffline() && printer.isDisconnected()">
    <div
      class="col-12 text-center py-2 text-warning"
    >
      <div>Printer is not connected to OctoPrint.</div>
      <button
        id="connect-printer"
        type="button"
        class="btn btn-outline-primary btn-block mt-2"
        :disabled="connecting"
        @click="this.onConnectClicked"
      >
        <b-spinner v-if="connecting" small></b-spinner>
        <i v-else class="fab fa-usb"></i>
        &nbsp;&nbsp;{{ connecting ? 'Contacting OctoPrint' : 'Connect' }}
      </button>
    </div>
  </div>
  <div class="row my-2" v-if="printer.isOffline()">
    <div
      class="col-12 text-center py-3 text-warning"
    >
      <div>
        OctoPrint is not powered on, or is offline.
        <a target="_blank" href="https://www.obico.io/docs/user-guides/octoprint-is-offline/">Why? <small><i class="fas fa-external-link-alt"></i></small></a>
      </div>
    </div>
  </div>
</div>
</template>

<script>

export default {
  name: 'PrinterActions',
  props: {
    printer: {},
  },
  data() {
    return {
      connectBtnClicked: false,
    }
  },
  computed: {
    connecting() {
      return this.connectBtnClicked && this.printer.isDisconnected()
    }
  },
  methods: {
    onPauseToggled(ev) {
      if (this.printer.isPaused()) {
        this.$emit('PrinterActionResumeClicked', ev)
      } else {
        this.$emit('PrinterActionPauseClicked', ev)
      }
    },
    onConnectClicked(ev) {
      this.$emit('PrinterActionConnectClicked', ev)
      this.connectBtnClicked = true
      setTimeout( () => {this.connectBtnClicked = false}, 10*1000)

    }
  }
}
</script>
