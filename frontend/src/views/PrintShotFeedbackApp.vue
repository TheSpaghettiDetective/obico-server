<template>
  <page-layout>
    <template #content>
      <b-container class="feedback-container">
        <b-row class="justify-content-center">
          <b-col lg="8">
            <div class="card">
              <h5 class="card-header text-center">
                F
                <i class="fas fa-search focused-feedback-icon"></i>{{$t("CUSED FEEDBACK")}}
              </h5>
              <loading :active="print === null" :is-full-page="true"></loading>
              <div v-if="print !== null">
                <focused-feedback-consent
                  v-if="!print.access_consented_at"
                  :print="print"
                  @continue-btn-pressed="consentBtnPressed"
                />
                <div v-else>
                  <div>
                    <vue-slick-carousel
                      ref="carousel"
                      :arrows="false"
                      :dots="true"
                      @afterChange="onNextShot"
                    >
                      <print-shot-card
                        v-for="(shot, i) in shots"
                        :key="i"
                        :shot="shot"
                        @shotChanged="onShotChanged"
                        @prev="onPrev"
                        @next="onNext"
                      ></print-shot-card>
                      <template #customPaging="page">
                        <div :class="pageClass(page)">&bull;</div>
                      </template>
                    </vue-slick-carousel>
                  </div>
                  <br />
                  <div class="card-body p-3">
                    <a :href="`/prints/${print.id}/`">
                      <i class="fas fa-chevron-left"></i> {{$t("Print Page")}}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
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
import PrintShotCard from '@src/components/print-shot-feedback/PrintShotCard'
import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import PageLayout from '@src/components/PageLayout'
import FocusedFeedbackConsent from '../components/print-shot-feedback/FocusedFeedbackConsent.vue'

export default {
  name: 'PrintShotFeedbackApp',
  components: {
    FocusedFeedbackConsent,
    Loading,
    PrintShotCard,
    VueSlickCarousel,
    PageLayout,
  },
  props: {
    config: {
      default: () => {},
      type: Object,
    },
  },
  data: function () {
    return {
      shots: [],
      currentShot: 0,
      print: null,
    }
  },
  computed: {},

  mounted() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      axios.get(urls.print(this.config.printId)).then((response) => {
        this.print = normalizedPrint(response.data)
        this.shots = sortBy(this.print.printshotfeedback_set, 'id')
      })
    },

    updatePrint(data) {
      axios
        .patch(urls.print(this.print.id), data)

        .then((response) => (this.print = response.data))
    },

    consentBtnPressed() {
      this.updatePrint({ access_consented_at: moment() })
    },

    onShotChanged(data) {
      const i = findIndex(this.shots, (shot) => shot.id == data.id)
      this.$set(this.shots, i, data)
      this.$refs.carousel.next()
    },

    onNextShot(shotIndex) {
      this.currentShot = shotIndex
    },

    onPrev() {
      this.$refs.carousel.prev()
    },

    onNext() {
      this.$refs.carousel.next()
    },

    pageClass(page) {
      if (page === this.currentShot) {
        return 'page-visiting'
      }
      return this.shots[page].answered_at ? 'text-success' : 'page-unvisited'
    },
  },
}
</script>

<style lang="sass" scoped>
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
  color: var(--color-primary)

.page-unvisited
  color: var(--color-divider)

.feedback-container
  padding-left: 30px
  padding-right: 30px
</style>
