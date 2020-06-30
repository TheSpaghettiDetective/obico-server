<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <div class="card">
        <h5 class="card-header text-center">
          F
          <i class="fas fa-search focused-feedback-icon"></i>CUSED FEEDBACK
        </h5>
        <loading :active="print === null" :is-full-page="true"></loading>
        <div v-if="print !== null">
          <consent
            v-if="!print.access_consented_at"
            :print="this.print"
            @continue-btn-pressed="this.consentBtnPressed"
          />
          <div v-else>
            <div>
              <vue-slick-carousel
                :arrows="true"
                :dots="true"
                @afterChange="onNextShot"
                ref="carousel"
              >
                <print-shot-card
                  v-for="(shot, i) in this.shots"
                  :key="i"
                  :shot="shot"
                  @shotChanged="onShotChanged"
                ></print-shot-card>
                <template #customPaging="page">
                  <div :class="pageClass(page)">&bull;</div>
                </template>
              </vue-slick-carousel>
            </div>
            <br />
            <div class="card-body p-3">
              <a href="/prints/">
                <i class="fas fa-chevron-left"></i> Time-lapse
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import sortBy from 'lodash/sortBy'
import findIndex from 'lodash/findIndex'
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
// optional style for arrows & dots
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'
// TODO: this should be configured as global. But for some reason it doesn't work.
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'

import Consent from './components/Consent'
import PrintShotCard from './components/PrintShotCard'
import apis from '../lib/apis'
import { normalizedPrint } from '../lib/normalizers'

export default {
  name: 'PrintShotFeedbackApp',
  components: {
    Consent,
    Loading,
    PrintShotCard,
    VueSlickCarousel
  },
  props: {
    config: {
      default: () => {},
      type: Object
    }
  },
  data: function() {
    return {
      shots: [],
      currentShot: 0,
      print: null
    }
  },
  computed: {},

  mounted() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      axios.get(apis.print(this.config.printId)).then(response => {
        this.print = normalizedPrint(response.data)
        this.shots = sortBy(this.print.printshotfeedback_set, 'id')
      })
    },

    updatePrint(data) {
      axios
        .patch(apis.print(this.print.id), data)

        .then(response => (this.print = response.data))
    },

    consentBtnPressed() {
      this.updatePrint({ access_consented_at: moment() })
    },

    onShotChanged(data) {
      const i = findIndex(this.shots, shot => shot.id == data.id)
      this.$set(this.shots, i, data)
      this.$refs.carousel.next()
    },

    onNextShot(shotIndex) {
      this.currentShot = shotIndex
    },

    pageClass(page) {
      if (page === this.currentShot) {
        return 'page-visiting'
      }
      return this.shots[page].answered_at ? 'text-success' : 'page-unvisited'
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.printshots-container
  padding: 1rem

.prev-btn
  display: inline
  position: absolute
  left: 2%
  top: 40%
  opacity: 0.5

.next-btn
  display: inline
  position: absolute
  right: 2%
  top: 40%
  opacity: 0.5

.page-visiting
  color: theme.$primary

.page-unvisited
  color: darken(theme.$secondary, 20)
</style>
