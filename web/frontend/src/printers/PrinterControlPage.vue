<template>
  <div class="container my-5">
    <div class="row justify-content-center" style="margin: -24px -31px 0px;">
      <div v-if="printer" :id="printer.id" :data-auth-token="printer.auth_token" class="col-sm-12 col-lg-8 printer-card">
        <div class="card">
          <div class="card-header">
            <div class="title-box">
              <div class="printer-name">{{ printer.name }}</div>
            </div>
          </div>
          <streaming-box :printer="printer" :isProAccount="isProAccount" />
          <div class="card-body" :class="{'overlay': !idle}">
            <div
              class="overlay-top text-center"
              style="left: 50%; margin-left: -102px; top: 50%; margin-top: -85px;"
              v-show="!idle"
            >
              <div>Printer controls are disabled</div>
              <div>because the printer is not idle.</div>
            </div>
            <div class="printer-controls">
              <div class="xy-controls">
                <button class="btn" type="button" data-axis="y" data-dir="up" @click="control(axis.y, directions.up)">
                  <i class="fas fa-angle-up fa-lg"></i>
                </button>
                <div class="x-controls">
                  <button class="btn" type="button" data-axis="x" data-dir="down" @click="control(axis.x, directions.down)">
                    <i class="fas fa-angle-left fa-lg"></i>
                  </button>
                  <button class="btn" type="button" data-axis="xy" data-dir="home" @click="control(axis.xy, directions.home)">
                    <i class="fas fa-home fa-lg"></i>
                  </button>
                  <button class="btn" type="button" data-axis="x" data-dir="up" @click="control(axis.x, directions.up)">
                    <i class="fas fa-angle-right fa-lg"></i>
                  </button>
                </div>
                <button class="btn" type="button" data-axis="y" data-dir="down" @click="control(axis.y, directions.down)">
                  <i class="fas fa-angle-down fa-lg"></i>
                </button>
              </div>
              <div class="z-controls">
                <button class="btn" type="button" data-axis="z" data-dir="up" @click="control(axis.z, directions.up)">
                  <i class="fas fa-angle-up fa-lg"></i>
                </button>
                <button class="btn" type="button" data-axis="z" data-dir="home" @click="control(axis.z, directions.home)">
                  <i class="fas fa-home fa-lg"></i>
                </button>
                <button class="btn" type="button" data-axis="z" data-dir="down" @click="control(axis.z, directions.down)">
                  <i class="fas fa-angle-down fa-lg"></i>
                </button>
              </div>
            </div>
            <br />
            <div class="control-options">
              <div class="btn-group btn-group-toggle" data-toggle="buttons">
                <label
                  class="btn"
                  v-for="option in jogDistanceOptions"
                  :key="option"
                  :class="{'active': jogDistance == option}"
                  @click="jogDistance = option"
                >
                  <input
                    type="radio"
                    name="jogDistance"
                    v-model="jogDistance"
                    :value="option"
                    autocomplete="off">
                  {{ option }}mm
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import urls from '@lib/server_urls'
  import { normalizedPrinter } from '@lib/normalizers'
  import StreamingBox from '@common/StreamingBox'
  import PrinterWebSocket from '@lib/printer_ws'
  import Janus from '@lib/janus'
  import webrtc from '@lib/webrtc_streaming'

  let printerWebRTCUrl = printerId => `/ws/janus/${printerId}/`
  let printerSharedWebRTCUrl = token => `/ws/share_token/janus/${token}/`

  const AXIS = {
    x: 'x',
    y: 'y',
    z: 'z',
    xy: ['x', 'y']
  }

  const DIRECTIONS = {
    up: 1,
    down: -1,
    home: 0
  }

  export default {
    name: 'PrinterControlPage',

    components: {
      StreamingBox,
    },

    data() {
      return {
        axis: AXIS,
        directions: DIRECTIONS,

        printer: null,

        // Current distance and possible options
        jogDistance: 10,
        jogDistanceOptions: [0.1, 1, 10, 100],

        // If false, controls are blocked
        idle: true,
      }
    },

    props: {
      printerId: {
        type: String,
        required: true,
      },
      isProAccount: {
        type: Boolean,
        required: true,
      },
      shareToken: {
        type: String,
        required: false
      },
    },

    mounted() {
      this.printerWs = PrinterWebSocket()

      this.fetchPrinter(this.printerId).then(() => {
        this.webrtc = null

        if (this.isProAccount) {
          Janus.init({
            debug: 'all',
            callback: this.onJanusInitalized
          })
        }
      })

      // Get jogDistance from localStorage or set default value
      const storageValue = localStorage.getItem(`mm-per-step-${this.printerId}`)
      this.jogDistance = storageValue ? storageValue : this.jogDistance
    },

    methods: {
      // Get printer info
      fetchPrinter() {
        return axios
          .get(urls.printer(this.printerId))
          .then(response => {
            this.printer = normalizedPrinter(response.data)
          })
      },

      // Control request after button click
      control(axis, direction) {
        let args = []
        let func = 'jog'

        if (direction === this.directions.home) {
          args.push(axis)
          func = 'home'
        } else {
          args.push({[axis]: direction * this.jogDistance})
        }

        const payload = {func: func, target: '_printer', args: args}
        const msgObj = this.printerWs.passThruToPrinter(this.printerId, payload)
        if (this.webrtc) {
          this.webrtc.sendPassThruMessage(msgObj)
        }
      },

      openWebRTCForPrinter() {
        let url, token
        if (this.shareToken) {
          url = printerSharedWebRTCUrl(this.shareToken)
          token = this.shareToken
        } else {
          url = printerWebRTCUrl(this.printerId)
          token = this.printer.auth_token
        }
        this.webrtc.connect(
          url,
          token
        )
      },

      onJanusInitalized() {
        if (!Janus.isWebrtcSupported()) {
          return
        }

        this.webrtc = webrtc.getWebRTCManager()
        this.openWebRTCForPrinter()
      },
    },

    watch: {
      jogDistance: function(newValue) {
        localStorage.setItem(`mm-per-step-${this.printerId}`, newValue)
      }
    },
  }
</script>

<style lang="sass" scoped>

</style>