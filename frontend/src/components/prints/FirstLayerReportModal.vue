<template>
    <div class="p-2">
      <b-row>
        <h4 class="mb-4 report-title">{{ $t("First Layer Report") }}</h4>
      </b-row>
      <b-row>
        <b-col lg="7">
          <!-- File Block Start -->
          <div class="file-block mb-3">
            <!-- File Block 1st row -->
            <div
              class="file-header compact"
              :class="{compact: compactView}"
            >
              <div v-if="showIconThumbnail">
                <div v-if="bigThumbnailUrl" class="thumbnail">
                  <img :src="bigThumbnailUrl" />
                </div>
                <div v-else class="thumbnail-placeholder">
                  <span class="help">
                    <help-widget id="thumbnail-setup-guide" :highlight="false" :show-close-button="false" />
                  </span>
                  <svg>
                    <use href="#svg-no-photo" />
                  </svg>
                </div>
              </div>
              <div v-else class="icon">
                <i class="fas fa-file-code"></i>
              </div>
              <div class="info truncated-wrapper">
                <div class="truncated" :title="file.filename">
                  {{ file.filename }}
                </div>
                <div v-if="file.filesize || file.deleted" class="subtitle text-secondary truncated-wrapper">
                  <div v-if="file.deleted" class="truncated">
                    <span class="text-danger">{{ $t("Deleted") }}</span>
                  </div>
                  <div v-else class="truncated">
                    <span>{{ file.filesize }}, {{$t("uploaded")}} {{ fileUploadedTime }}</span>
                  </div>
                </div>
              </div>
              <div class="button">
                  <b-button
                    :href="`/g_code_files/cloud/${file.id}/`"
                    v-if="showOpenButton && file.id"
                  >
                    {{$t("Open File")}}
                  </b-button>
                </div>
            </div>
            <!-- File Block 2nd row -->
            <div class="first-layer-report-info-line">
              <div class="label">
                <div class="icon"><i class="fas fa-info"></i></div>
                <div>{{ $t("First Layer Grade") }}</div>
              </div>
              <div class="value">
                <div :class="gradeResult.gradeAccent">
                  {{ gradeResult.gradeTitle || '&nbsp;' }}
                </div>
              </div>
            </div>
            <!-- File Block 3rd row -->
            <div class="first-layer-report-info-line">
              <div class="label">
                <div class="icon"><i class="far fa-clock"></i></div>
                <div>{{ $t("First Layer Print Time") }}</div>
              </div>
              <div class="value">{{ firstLayerPrintTime }}</div>
            </div>
          </div>

          <!-- File Block End -->
          <!-- Notes Block Start -->
          <div class="notes-block mb-3">
            <!-- Notes Block 1st row -->
            <b-row>
              <span class="title">{{ $t("First Layer Notes") }}</span>
            </b-row>
            <hr />
            <!-- File Block 2nd row -->
            <b-row>
              <div class="description">
                <p>
                  {{ $t("You're first layer score is") }}:
                   <span class="font-bold" :class="gradeResult.gradeAccent">{{ gradeResult.grade }}</span><br>
                  {{ gradeResult.gradeRemarks }}
                </p>
              </div>
            </b-row>
            <hr v-if="!isGradeA" />
            <!-- File Block 3rd row -->
            <b-row>
              <div v-if="!isGradeA" class="info">
                <p>
                  <i18next :translation="$t(`Grade {localizedDom} usually means one of the following`)">
                    <template #localizedDom>
                      <span :class="gradeResult.gradeAccent">{{gradeResult.grade}}</span>
                    </template>
                  </i18next>
                </p>
                <ul>
                  <li v-for="(suggestion, index) in gradeResult.gradeSuggestion" :key="index" v-html="suggestion"></li>
                </ul>
              </div>
            </b-row>
          </div>
        </b-col>
        <!-- Map Section -->
        <b-col lg="5" class="heatmap-column">
          <b-card no-body>
            <b-tabs pills card>
              <b-tab :title="$t('AI Time-Lapse')">
                <b-card-text>
                  <div class="first-layer-modal-video-wrapper">
                    <video-box
                      :video-url="firstLayerInspection.tagged_video_url"
                      :poster-url="aiTimeLapsePosterImageUrl"
                      :fluid="false"
                      :fullscreen-btn="false"
                      :download-btn="true"
                      :default-full-screen-toggle="true"
                      @download="
                        () => downloadFile(firstLayerInspection.tagged_video_url, `${print.id}_tagged_video_inspection.mp4`)
                      "
                    />
                  </div>
                </b-card-text>
              </b-tab>
              <b-tab :title="$t('Original Time-Lapse')">
                <b-card-text>
                  <div class="first-layer-modal-video-wrapper">
                    <video-box
                      :video-url="firstLayerInspection.video_url"
                      :poster-url="firstLayerInspection.images.length ? firstLayerInspection.images[0].image_url : null"
                      :fluid="false"
                      :fullscreen-btn="false"
                      :download-btn="true"
                      :default-full-screen-toggle="true"
                      @download="
                        () => downloadFile(firstLayerInspection.video_url, `${print.id}_video_inspection.mp4`)
                      "
                    />
                  </div>
                </b-card-text>
              </b-tab>
            </b-tabs>
          </b-card>
          
        </b-col>
      </b-row>
      <b-row class="buttons-row">
        <!-- Notes Block End -->
        <b-col cols="12" lg="7">
            <a :href="`/first_layer_inspection_images/?print_id=${print.id}`" class="feedback-button">{{ $t("Give Feedback About This Report") }}</a
            >
        </b-col>
      </b-row>
    </div>
</template>

<script>
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'
import 'vue-loading-overlay/dist/vue-loading.css'
import PageLayout from '@src/components/PageLayout'
import VideoBox from '@src/components/VideoBox'
import { downloadFile } from '@src/lib/utils'

export default {
  name: 'FirstLayerReportModal',
  components: {
    VueSlickCarousel,
    PageLayout,
    VideoBox
  },

  data: function () {
    return {
      showCarouselAnimation: true,
      first_layer_info: {},
      carouselItems: [],
      settings: {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 1,
        slidesToScroll: 1,
        adaptiveHeight: true,
        initialSlide: 0,
      },
      activeTab: 0,
      carouselKey: 0,
      activeThumbnail: null,
      thumbnailStyle: {
        width: '150px',
        height: '150px',
        position: 'absolute',
        zIndex: '1070',
      },
    }
  },
  props: {
    firstLayerInspection: {
      type: Object,
      required: true,
    },
    firstLayerPrintTime: {
      type: String,
      required: true
    },
    gradeResult: {
      type: Object,
      required: true,
    },
    print: {
      type: Object,
      required: true,
    },
    showOpenButton: {
      type: Boolean,
      default: false,
    },
    compactView: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    aiTimeLapsePosterImageUrl() {
      if (this.firstLayerInspection.poster_url) {
        return this.firstLayerInspection.poster_url
      }
      return this.firstLayerInspection.images?.length ? this.firstLayerInspection.images[0].image_url : null
    },
    file() {
      return this.print.g_code_file || { filename: this.print.filename }
    },
    isGradeA() {
      return this.gradeResult.grade === 'A'
    },
    showIconThumbnail() {
      return !this.compactView || this.bigThumbnailUrl
    },
    bigThumbnailUrl() {
      return this.file.getBigThumbnailUrl && this.file.getBigThumbnailUrl()
    },
    fileUploadedTime() {
      return this.file.created_at.fromNow()
    },
  },
  watch: {
    firstLayerInfo: {
      handler: function (value) {
        if (value) {
          this.prepareFirstLayerInfo()
        }
      },
      immediate: true,
    },
  },
  methods: {
    downloadFile,
  },
}
</script>

<style lang="sass" scoped>
.buttons-row
  @media (max-width: 991px)
    margin-top: 2em
.heatmap-column
  display: flex
  flex-direction: column
  align-items: center
  .card
    background-color: var(--color-background)
    border-radius: var(--border-radius-lg)
.file-header
  display: flex
  align-items: center
  gap: 1rem
  padding-bottom: 5px
  .info
    flex: 1
  .icon
    flex: 0 0 2rem
    text-align: center
    *
      font-size: 2rem
.font-bold
  font-weight: bold
.first-layer-report-info-line
  display: flex
  align-items: center
  justify-content: space-between
  margin-bottm: 6px
  padding: 6px 0
  gap: .5rem
  border-top: 1px solid var(--color-divider-muted)
  &:first-of-type
    border-top: none
  .label
    display: flex
    align-items: center
    flex: 1
    gap: .5rem
    line-height: 1.1
    .icon
      opacity: .5
      width: 1rem
      text-align: center
  .value
    font-weight: bold

.report-title
  padding-left: 15px

.feedback-button
  border: 1px solid var(--color-primary)
  display: block
  text-align: center
  border-radius: 17px
  padding: 8px
  color: var(--color-primary)
  background-color: transparent
  &:hover
    background-color: var(--color-hover)
hr
  width: 100%
  margin-top: 7px
  margin-bottom: 7px
.notes-block
  background-color: var(--color-background)
  padding: 1.5em
  border-radius: var(--border-radius-lg)

  display: flex
  flex-direction: column
  .title
    padding: 0 1em
  .description
    padding: 0 1em
    font-size: 0.9em
    p
      margin: 0
  .info
    padding: 0 1em
    font-size: 0.9em
    p
      margin: 0
    ul
      margin: 0 -15px
      li
        font-size: 0.9em


.file-block
  background-color: var(--color-background)
  padding: 1.5em
  border-radius: var(--border-radius-lg)
  display: flex
  flex-direction: column
  .title
    width:100%
    display: flex
    padding: 0 1em
    font-size: 1.125rem
    color: var(--color-text-primary)
    font-weight: medium
    span
      margin-left: .5em
    .icon
      flex: 1
      display: flex
      align-items: center
      i
        font-size: 2em
    .info
      flex: 15
      font-size: 1rem
      grid-column: span 1
      .file-size
        color: var(--color-divider)
    .button
      display: flex
      align-items: center
      justify-content: flex-end
  @media (max-width: 768px)
    grid-template-columns: 8% 60% 32%
  .first-layer-grade
    width:100%
    display: flex
    justify-content: space-between
    align-items: center
    padding: 0 1em
    .icon
      flex: 1
      display: flex
      align-items: center
      justify-content: center
    .name
      flex: 15
      @media (max-width: 768px)
        flex: 11
    .status
      display: flex
      justify-content: flex-end
  .first-layer-print-time
    width:100%
    display: flex
    justify-content: space-between
    padding: 0 1em
    grid-template-columns: 3% 67% 30%
    .icon
      flex: 1
      display: flex
      align-items: center
      justify-content: center

    .name
      flex: 18
      @media (max-width: 768px)
        flex: 15
    .status
      display: flex
      justify-content: flex-end

  &.bar-chart
    height: auto
    .chart-wrapper
      height: 210px
  @media (max-width: 768px)
    padding: 1.25em 1.5em


.dark-icon
  color: var(--color-divider)


$border-color: #dee2e6
.card-map
  border-radius: var(--border-radius-lg)
  background: white
  @media (min-width: 991px)
    max-width: 490px
  .card-body
    padding: 10%
    
.border-right
  border-right: 1px solid $border-color

.transparent-button
  background-color: transparent
  border-color: #007bff
  color: #007bff
  &:hover
    background-color: rgba(#007bff, 0.1)




@media (max-width: 768px)
  .file-block-title
    grid-template-columns: 7% 65% 28%

  @media (max-width: 1198px)
    .file-block-title
      grid-template-columns: 7% 65% 28%

.is-fullscreen
  position: fixed
  top: 0
  left: 0
  bottom: 0
  right: 0
  z-index: 9999
  background-color: var(--color-background)
  display: flex
  flex: 1
  order: 1
  ::v-deep .video-js
    height: 100vh !important
</style>

<style>
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
.carousel-active-tab {
  border: none !important;
  background-color: var(--color-background) !important;
}
.carousel-tab {
  &:hover {
    background-color: var(--color-hover);
  }
}
div#carousal-modal {
  animation: swal2-show .3s !important;
  transition: none !important;
}
.modal-dialog.modal-lg {
  transition: none !important
}
div#carousal-modal___BV_modal_outer_ {
  z-index: 1100 !important;
}

button.btn.feedback-button.btn-secondary {
  border: 1px solid var(--color-primary) !important
}
</style>
