<template>
  <div>
    <pull-to-reveal>
      <navbar view-name="publictimelapse_list"></navbar>
    </pull-to-reveal>

    <div class="timelapse-gallery">

      <!-- Header -->
      <div class="row">
        <div class="col-sm-12 text-center">
          <h1>Spaghetti Gallery</h1>
        </div>
      </div>
      <div class="row">
        <div class="col-sm-12 hints">
          The Spaghetti Detective is still in early stage and its algorithm is not perfect yet. It may sometimes give
          false alarms, or miss print failures.
          So we compiled this "Spaghetti Gallery" to show you that some camera setups (angle, lighting, etc) are better
          than others at helping the Detective do the job.
        </div>
      </div>

      <!-- Timelapses -->
      <div class="row">
        <print-card
          v-for="timelapse of pageTimelapses"
          :key="timelapse.id"
          :print="timelapse"
          :isPublic="true"
          @fullscreen="openFullScreen"
        ></print-card>
      </div>

      <!-- Timelapses loader on scroll down -->
      <mugen-scroll :handler="fetchMoreData" :should-handle="!loading" class="text-center p-4">
        <div v-if="noMoreData" class="text-center p-2">End of public time-lapse list.</div>
        <b-spinner v-if="!noMoreData" label="Loading..."></b-spinner>
      </mugen-scroll>

      <!-- Full-screen timelapse -->
      <b-modal
        id="tl-fullscreen-modal"
        size="full"
        @hidden="fullScreenClosed"
        :title="fullScreenPrintTitle"
        :hideFooter="true"
      >
        <full-screen-print-card
          :print="fullScreenPrint"
          :videoUrl="fullScreenPrintVideoUrl"
          :autoplay="true"
          :is-public="true"
        />
      </b-modal>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import urls from '../lib/server_urls'
  import Navbar from '@common/Navbar.vue'
  import PullToReveal from '@common/PullToReveal.vue'
  import PrintCard from './PrintCard.vue'
  import FullScreenPrintCard from './FullScreenPrintCard.vue'
  import findIndex from 'lodash/findIndex'
  import MugenScroll from 'vue-mugen-scroll'

  export default {
    name: 'PublicTimelapsesPage',

    components: {
      Navbar,
      PullToReveal,
      PrintCard,
      FullScreenPrintCard,
      MugenScroll,
    },

    data() {
      return {
        perLoad: 6,
        loadsNumber: 1,
        timelapses: [],
        fullScreenPrint: null,
        fullScreenPrintVideoUrl: null,
        noMoreData: false,
        loading: false,
      }
    },

    created() {
      axios
        .get(urls.publicTimelapse())
        .then(response => {
          for (const timelapse of response.data) {
            this.timelapses.push(this.adaptTimelapseToPrint(timelapse))
          }
        })
    },

    computed: {
      pageTimelapses() {
        const end = (this.loadsNumber - 1) * this.perLoad + this.perLoad
        return this.timelapses.slice(0, end)
      },

      fullScreenPrintTitle() {
        if (this.fullScreenPrint) {
          return `- By ${this.fullScreenPrint.creator_name}`
        }

        return ''
      }
    },

    methods: {
      openFullScreen(printId, videoUrl) {
        const i = findIndex(this.timelapses, p => p.id == printId)
        if (i != -1) {
          this.fullScreenPrint = this.timelapses[i]
          this.fullScreenPrintVideoUrl = videoUrl
          this.$bvModal.show('tl-fullscreen-modal')
        }
      },

      fullScreenClosed() {
        this.fullScreenPrint = null
        this.fullScreenPrintVideoUrl = null
      },

      fetchMoreData() {
        if (this.noMoreData) {
          return
        }

        this.loading = true
        setTimeout(() => {
          this.loadsNumber++
          this.loading = false
          if (this.timelapses.length <= (this.loadsNumber * this.perLoad)) {
            this.noMoreData = true
          }
        }, 500)
      },

      // TODO: remove after API fix
      adaptTimelapseToPrint(timelapse) {
        timelapse.prediction_json_url = timelapse.p_json_url
        delete timelapse.p_json_url
        return timelapse
      },
    }
  }
</script>

<style lang="sass" scoped>
::v-deep .pagination-wrapper button
  border-radius: 0

::v-deep #tl-fullscreen-modal
  .modal-full
    max-width: 100%
    margin: 0

  .video-js
    height: 0
    height: calc(100vh - 243px)
</style>
