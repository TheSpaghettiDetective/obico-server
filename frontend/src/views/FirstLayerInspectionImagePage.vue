<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row>
          <b-col>
            <h2 class="text-center">{{ $t('First Layer Snapshots') }}</h2>
            <p class="my-4">
              {{$t("Help {brandName}'s First Layer AI (codename: Celestrius) learn and improve quickly by telling her what issues exist in each of these snapshots.",{brandName:$syndicateText.brandName})}}
            </p>
            <p class="text-secondary">{{ $t('Why should I do this?') }}</p>
            <p class="text-secondary small">
              {{$t("{brandName}'s First Layer AI is still in her infant time. Just like a human baby, the only way she can learn is to be told by adults what is good and what is bad. By telling her what issues exist in these snapshots, you will help her get better at telling a good first layer apart from a bad one.",{brandName:$syndicateText.brandName})}}
            </p>
            <p class="small">
              <i
                >
                {{ $t("Privacy Notice: By participating in this survey, you grant the {brandName} team members the permission to review all snapshots below.",{brandName:$syndicateText.brandName}) }}
                </i
              >
            </p>
            <h5 class="text-primary mt-4">{{ $t('Earn 3 AI Detection Hours!') }}</h5>
            <p class="text-primary mb-5">
              {{ $t("{name} snapshots were selected from your first layer print. Earn 3 AI Detection Hours by telling us if you see any printing issues with these snapshots!",{name:shots.length}) }}
            </p>
          </b-col>
        </b-row>
        <b-row class="feedback-card">
          <b-col md="8" lg="6">
            <div class="card">
              <loading :active="firstLayerInspection === null" :is-full-page="true"></loading>
              <div v-if="firstLayerInspection !== null">
                <div>
                  <div>
                    <vue-slick-carousel
                      ref="carousel"
                      :arrows="false"
                      :dots="true"
                      @afterChange="onNextShot"
                    >
                      <first-layer-shot-card
                        v-for="(shot, i) in shots"
                        :key="i"
                        :shot="shot"
                        :shot-index="i"
                        :total-shots="shots.length"
                        @imageUpdated="onImageUpdated"
                        @prev="onPrev"
                        @next="onNext"
                      ></first-layer-shot-card>
                      <template #customPaging="page">
                        <div :class="pageClass(page)">&bull;</div>
                      </template>
                    </vue-slick-carousel>
                  </div>
                  <br />
                  <div class="card-body p-3"></div>
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
import urls from '@config/server-urls'
import findIndex from 'lodash/findIndex'
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'
import PageLayout from '@src/components/PageLayout'
import FirstLayerShotCard from '@src/components/first-layer-review/FirstLayerShotCard.vue'

export default {
  name: 'FirstLayerInspectionImagePage',
  components: {
    Loading,
    FirstLayerShotCard,
    VueSlickCarousel,
    PageLayout,
  },

  data: function () {
    return {
      shots: [],
      currentShot: 0,
      firstLayerInspection: null,
      inspectionId: null,
    }
  },
  computed: {},

  mounted() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      const urlParts = window.location.pathname.split('/')
      this.inspectionId = urlParts[urlParts.length - 2]

      const urlParams = new URLSearchParams(window.location.search)
      this.inspectionId = urlParams.get('print_id')

      axios.get(urls.firstLayerInspection(this.inspectionId)).then((response) => {
        if (response.data.length) {
          this.firstLayerInspection = response.data[0]
          this.shots = this.firstLayerInspection.images.sort((a, b) => a.id - b.id)
        }
      })
    },

    onImageUpdated(data) {
      const i = findIndex(this.shots, (shot) => shot.id == data.id)
      this.$set(this.shots, i, data)
      const { credited_dhs } = data

      if (credited_dhs > 0) {
        this.$swal.Prompt.fire({
          title: `${this.$i18next.t('You just earned 3 AI Detection Hours!')}`,
          html: `<p>${this.$i18next.t("Having more training data is crucial for a better First Layer AI. Thank you!")}</p><p>${this.$i18next.t("You can now close this page")}.</p>`,
          confirmButtonText: `${this.$i18next.t('Okay!')}`,
        })
      }
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

.cardH
  align-items: center
  justify-content: center
  display: flex
  gap: 5px

.feedback-card
  justify-content: center
</style>
