<template>
  <div>
    <pull-to-reveal :enable="false">
      <navbar view-name="publictimelapse_list"></navbar>
    </pull-to-reveal>

    <div class="timelapse-gallery">
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

      <!-- Top pagination -->
      <!-- <div class="row mb-3">
        <div class="col-sm-12 pagination-wrapper">
          <b-pagination
            v-model="currentPage"
            :total-rows="rows"
            :per-page="perPage"
          ></b-pagination>
        </div>
      </div> -->

      <!-- Timelapses -->
      <div class="row">
        <print-card
          v-for="timelapse of timelapses"
          :key="timelapse.id"
          :print="timelapse"
          :isPublic="true"
          @fullscreen="openFullScreen"
        ></print-card>
      </div>

      <mugen-scroll :handler="fetchMoreData" :should-handle="!loading" class="text-center p-4">
        <div v-if="noMoreData" class="text-center p-2">End of your time-lapse list.</div>
        <b-spinner v-if="!noMoreData" label="Loading..."></b-spinner>
      </mugen-scroll>

      <!-- Top pagination -->
      <!-- <div class="row my-3">
        <div class="col-sm-12 pagination-wrapper">
          <b-pagination
            v-model="currentPage"
            :total-rows="rows"
            :per-page="perPage"
          ></b-pagination>
        </div>
      </div> -->

      <!-- Full-screen timelapse -->
      <b-modal
        id="tl-fullscreen-modal"
        size="full"
        @hidden="fullScreenClosed"
        :hideHeader="true"
        :hideFooter="true"
      >
        <full-screen-print-card
          :print="fullScreenPrint"
          :videoUrl="fullScreenPrintVideoUrl"
          :autoplay="true"
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
        perPage: 6,
        currentPage: 1,
        timelapses: [],
        fullScreenPrint: null,
        fullScreenPrintVideoUrl: null,
        noMoreData: false,
        loading: false,
      }
    },

    created() {
      this.fetchMoreData()
      // axios
      //   .get(urls.publicTimelapse())
      //   .then(response => {
      //     for (const timelapse of response.data) {
      //       this.timelapses.push(this.adaptTimelapseToPrint(timelapse))
      //     }
      //     // this.timelapses = response.data
      //     // console.log('loaded:')
      //     // console.log(response)
      //   })
    },

    computed: {
      pageTimelapses() {
        const start = (this.currentPage - 1) * this.perPage
        const end = start + this.perPage
        return this.timelapses.slice(start, end)
      },
      rows() {
        return this.timelapses.length
      },
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


      // TODO: remove
      adaptTimelapseToPrint(timelapse) {
        timelapse.prediction_json_url = timelapse.p_json_url
        delete timelapse.p_json_url
        return timelapse
      },

      fetchMoreData() {
        if (this.noMoreData) {
          return
        }

        this.loading = true
        axios
          .get(urls.publicTimelapse(), {
            params: {
              start: this.timelapses.length,
              limit: this.perPage,
            }
          })
          .then(response => {
            console.log('data:')
            console.log(response)

            this.loading = false
            this.noMoreData = response.data.length < this.perPage
            for (const timelapse of response.data) {
              this.timelapses.push(this.adaptTimelapseToPrint(timelapse))
            }
          })
      },
    }
  }
</script>

<style lang="sass" scoped>
::v-deep .pagination-wrapper button
  border-radius: 0
</style>