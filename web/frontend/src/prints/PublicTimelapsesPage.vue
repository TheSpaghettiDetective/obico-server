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
      <div class="row mb-3">
        <div class="col-sm-12 pagination-wrapper">
          <b-pagination
            v-model="currentPage"
            :total-rows="rows"
            :per-page="perPage"
          ></b-pagination>
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

      <!-- Top pagination -->
      <div class="row my-3">
        <div class="col-sm-12 pagination-wrapper">
          <b-pagination
            v-model="currentPage"
            :total-rows="rows"
            :per-page="perPage"
          ></b-pagination>
        </div>
      </div>

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
  import Navbar from '@common/Navbar.vue'
  import PullToReveal from '@common/PullToReveal.vue'
  import PrintCard from './PrintCard.vue'
  import FullScreenPrintCard from './FullScreenPrintCard.vue'
  import findIndex from 'lodash/findIndex'
  
  export default {
    name: 'PublicTimelapsesPage',

    components: {
      Navbar,
      PullToReveal,
      PrintCard,
      FullScreenPrintCard,
    },

    data() {
      return {
        perPage: 9,
        currentPage: 1,
        timelapses: [
          {
            id: 48,
            title: 'T-00207.mp4',
            priority: 1,
            video_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00207.mp4',
            poster_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00207.mp4.poster.jpg',
            prediction_json_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00207.mp4.json',
            creator_name: 'Lila',
            uploaded_by_id: null,
            created_at: '2019-02-02T21:21:08.307Z',
            updated_at: '2020-01-23T21:17:52.731Z',
            printshotfeedback_set: [],
          },
          {
            id: 2,
            title: 'T-00002.mp4',
            priority: 2,
            video_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00002.mp4',
            poster_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00002.mp4.poster.jpg',
            prediction_json_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00002.mp4.json',
            creator_name: 'Kenneth',
            uploaded_by_id: null,
            created_at: '2019-02-02T21:01:22.977Z',
            updated_at: '2020-01-23T21:17:50.691Z',
            printshotfeedback_set: [],
          },
          {
            id: 43,
            title: 'T-00202.mp4',
            priority: 3,
            video_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00202.mp4',
            poster_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00202.mp4.poster.jpg',
            prediction_json_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00202.mp4.json',
            creator_name: 'Jimmy',
            uploaded_by_id: null,
            created_at: '2019-02-02T21:15:39.060Z',
            updated_at: '2020-01-23T21:17:54.989Z',
            printshotfeedback_set: [],
          },
          {
            id: 47,
            title: 'T-00206.mp4',
            priority: 4,
            video_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00206.mp4',
            poster_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00206.mp4.poster.jpg',
            prediction_json_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00206.mp4.json',
            creator_name: 'Jimmy',
            uploaded_by_id: null,
            created_at: '2019-02-02T21:16:32.870Z',
            updated_at: '2020-01-23T21:17:52.653Z',
            printshotfeedback_set: [],
          },
          {
            id: 4,
            title: 'T-00004.mp4',
            priority: 5,
            video_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00004.mp4',
            poster_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00004.mp4.poster.jpg',
            prediction_json_url: 'https://tsd-pub-static.s3.amazonaws.com/pub-tls/T-00004.mp4.json',
            creator_name: 'Kenneth',
            uploaded_by_id: null,
            created_at: '2019-02-02T21:02:06.115Z',
            updated_at: '2020-01-23T21:17:50.818Z',
            printshotfeedback_set: [],
          },
        ],
        fullScreenPrint: null,
        fullScreenPrintVideoUrl: null,
      }
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
      }
    }
  }
</script>

<style lang="sass" scoped>
::v-deep .pagination-wrapper button
  border-radius: 0
</style>