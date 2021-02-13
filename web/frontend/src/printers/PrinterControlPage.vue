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
          <div class="card-body">
            <div class="overlay-top text-center"
              style="left: 50%; margin-left: -102px; top: 50%; margin-top: -85px; display: none"
            >
              <div>Printer controls are disabled</div>
              <div>because the printer is not idle.</div>
            </div>
            <div class="printer-controls">
              <div class="xy-controls">
                <button class="btn" type="button" data-axis="y" data-dir="up">
                  <i class="fas fa-angle-up fa-lg"></i>
                </button>
                <div class="x-controls">
                  <button class="btn" type="button" data-axis="x" data-dir="down">
                    <i class="fas fa-angle-left fa-lg"></i>
                  </button>
                  <button class="btn" type="button" data-axis="xy" data-dir="home">
                    <i class="fas fa-home fa-lg"></i>
                  </button>
                  <button class="btn" type="button" data-axis="x" data-dir="up">
                    <i class="fas fa-angle-right fa-lg"></i>
                  </button>
                </div>
                <button class="btn" type="button" data-axis="y" data-dir="down">
                  <i class="fas fa-angle-down fa-lg"></i>
                </button>
              </div>
              <div class="z-controls">
                <button class="btn" type="button" data-axis="z" data-dir="up">
                  <i class="fas fa-angle-up fa-lg"></i>
                </button>
                <button class="btn" type="button" data-axis="z" data-dir="home">
                  <i class="fas fa-home fa-lg"></i>
                </button>
                <button class="btn" type="button" data-axis="z" data-dir="down">
                  <i class="fas fa-angle-down fa-lg"></i>
                </button>
              </div>
            </div>
            <br />
            <div class="control-options">
              <div class="btn-group btn-group-toggle" data-toggle="buttons">
                <label class="btn">
                  <input type="radio" name="jog-distance" value="0.1" autocomplete="off">0.1mm
                </label>
                <label class="btn">
                  <input type="radio" name="jog-distance" value="1" autocomplete="off">1mm
                </label>
                <label class="btn">
                  <input type="radio" name="jog-distance" value="10" autocomplete="off">10mm
                </label>
                <label class="btn">
                  <input type="radio" name="jog-distance" value="100" autocomplete="off">100mm
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

  export default {
    name: 'PrinterControlPage',

    components: {
      StreamingBox,
    },

    data() {
      return {
        printer: null
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
    },

    mounted() {
      this.fetchPrinter(this.printerId)
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
    },
  }
</script>

<style lang="sass" scoped>

</style>