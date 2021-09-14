<template>
  <layout>
    <template v-slot:content>
      <div class="container my-5">
        <div class="row justify-content-center" style="margin: -24px -31px 0px;">
          <div v-if="printer" class="col-sm-12 col-lg-8 printer-card">
            <div class="card">
              <div class="card-header">
                <div class="title-box">
                  <div class="printer-name">{{ printer.name }}</div>
                </div>
              </div>
              <streaming-box :printer="printer" :webrtc="webrtc" />
              <div class="card-body" :class="{'overlay': !printer.isIdle()}">
                <div
                  class="overlay-top text-center"
                  style="left: 0; width: 100%; top: 50%; margin-top: -85px;"
                  v-show="!printer.isIdle()"
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
                  <b-form-group v-slot="{ ariaDescribedby }">
                    <b-form-radio-group
                      v-model="jogDistance"
                      :options="jogDistanceOptions.map(val => { return {text: val + 'mm', value: val} })"
                      name="jogDistance"
                      button-variant="default"
                      :aria-describedby="ariaDescribedby"
                      buttons
                    ></b-form-radio-group>
                  </b-form-group>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </layout>
</template>

<script>
  import split from 'lodash/split'
  import urls from '@lib/server_urls'
  import { normalizedPrinter } from '@lib/normalizers'
  import StreamingBox from '@common/StreamingBox'
  import PrinterComm from '@lib/printer_comm'
  import WebRTCConnection from '@lib/webrtc'
  import Layout from '@common/Layout.vue'
  import { isLocalStorageSupported } from '@common/utils'
  import { user } from '@lib/page_context'

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
      Layout,
    },

    data() {
      return {
        axis: AXIS,
        directions: DIRECTIONS,

        user: null,
        printerId: null,
        printer: null,
        webrtc: null,

        // Current distance and possible options
        jogDistance: 10,
        jogDistanceOptions: [0.1, 1, 10, 100],
      }
    },

    created() {
      this.user = user()
      this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()

      // Get jogDistance from localStorage or set default value
      const storageValue = isLocalStorageSupported() ? localStorage.getItem(`mm-per-step-${this.printerId}`) : null
      this.jogDistance = storageValue ? storageValue : this.jogDistance

      this.webrtc = WebRTCConnection(this.user.is_pro)

      this.printerComm = PrinterComm(
        this.printerId,
        urls.printerWebSocket(this.printerId),
        (data) => {
          this.printer = normalizedPrinter(data, this.printer)
          if (this.webrtc && !this.webrtc.initialized) {
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)
          }
        }
      )
      this.printerComm.connect()
    },

    methods: {
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
        this.printerComm.passThruToPrinter(payload)
      },
    },

    watch: {
      jogDistance: function(newValue) {
        if (isLocalStorageSupported()) {
          localStorage.setItem(`mm-per-step-${this.printerId}`, newValue)
        }
      }
    },
  }
</script>

<style lang="sass" scoped>
::v-deep .control-options .btn
  color: rgb(var(--color-text-primary))
</style>
