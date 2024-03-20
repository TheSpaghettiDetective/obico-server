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
              <div class="value">{{ print.duration || '-' }}</div>
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
                  {{ $t("You're first layer score is:") }}
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
                  <i18next :translation="$t(`Grade {domLink} usually means one of the following:`)">
                    <template #domLink>
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
          <b-card no-body class="mb-3 text-center card-map">
            <b-card-body>
              <div ref="imageContainer" class="image-container">
                <b-img
                  :src="
                    isHeatmapVisible
                      ? first_layer_info.heatmap_img_url
                      : first_layer_info.gcode_img_url
                  "
                  alt="First Layer Map"
                />

                <button class="toggle-heatmap" @click="toggleHeatmap">
                  <i
                    :class="`fa ${isHeatmapVisible ? 'fa-eye' : 'fa-eye-slash'}`"
                    aria-hidden="true"
                  ></i>
                </button>

                <div v-if="isHeatmapVisible">
                  <div
                    v-for="(point, index) in first_layer_info.points"
                    :key="index"
                    class="pin"
                    :style="{ left: `${point.x_percent}%`, top: `${point.y_percent}%` }"
                    @click="isHeatmapVisible ? imageClicked(point) : null"
                    @mouseover="isHeatmapVisible ? showThumbnail(point, $event) : null"
                    @mouseleave="isHeatmapVisible ? hideThumbnail() : null"
                  ></div>
                </div>

                <div v-if="activeThumbnail" :style="thumbnailStyle" class="thumbnail">
                  <img :src="activeThumbnail" />
                </div>

                <!-- Carousal Modal Start -->
                <b-modal
                  id="carousal-modal"
                  size="lg"
                  hide-footer
                  hide-header
                  content-class="b-carousel"
                  class="b-carousel"
                  @show="onCarouselModalShow"
                >
                  <button @click="closeCarousel" class="close-carousel">×</button>
                  <div class="carousel-tabs">
                    <b-tabs
                      v-model="activeTab"
                      nav-class="mb-2 border-0"
                      active-nav-item-class="carousel-active-tab"
                    >
                      <b-tab
                        title="AI Detected Image"
                        active
                        title-link-class="carousel-tab"
                        @click="handleTabClicked"
                      >
                        <vue-slick-carousel
                          v-if="carouselItems.length"
                          ref="slickTagged"
                          v-bind="settings"
                          class="custom-slick-carousel"
                          @afterChange="afterCarouselImageChanged"
                          @beforeChange="beforeCarouselImageChanged"
                        >
                          <img
                            v-for="(item, index) in carouselItems"
                            :key="`tagged-${index}`"
                            width="auto"
                            height="350px"
                            :class="{ 'fade-in': showCarouselAnimation }"
                            :src="item.tagged_img_url"
                            :alt="`Tagged Screenshot ${index + 1}`"
                          />
                        </vue-slick-carousel>
                      </b-tab>

                      <b-tab title="Original Image" title-link-class="carousel-tab" @click="handleTabClicked">
                        <vue-slick-carousel
                          v-if="carouselItems.length"
                          ref="slickOriginal"
                          v-bind="settings"
                          class="custom-slick-carousel"
                          @afterChange="afterCarouselImageChanged"
                          @beforeChange="beforeCarouselImageChanged"
                        >
                          <img
                            v-for="(item, index) in carouselItems"
                            :key="`original-${index}`"
                            width="auto"
                            height="350px"
                            :class="{ 'fade-in': showCarouselAnimation }"
                            :src="item.raw_img_url"
                            :alt="`Original Screenshot ${index + 1}`"
                          />
                        </vue-slick-carousel>
                      </b-tab>
                    </b-tabs>
                  </div>
                </b-modal>
                <!-- Carousal Modal End -->
              </div>
            </b-card-body>
          </b-card>
          <div class="map-info">
            {{$t("Click pins on the g-node map to see snapshots of certain areas of the print.")}}
          </div>
        </b-col>
      </b-row>
      <b-row class="buttons-row">
        <!-- Notes Block End -->
        <b-col cols="12" lg="7">
          <b-button class="mb-3" style="width: 100%"
            >{{ $t("View First Layer Timelapse") }}</b-button
          >
          <b-button class="feedback-button" style="width: 100%"
            >{{ $t("Give Feedback About This Report") }}</b-button
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

export default {
  name: 'FirstLayerReportModal',
  components: {
    VueSlickCarousel,
    PageLayout,
  },

  data: function () {
    return {
      showCarouselAnimation: true,
      first_layer_info: {},
      carouselItems: [],
      isHeatmapVisible: true,
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
    firstLayerInfo: {
      type: Object,
      required: true,
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
    onCarouselModalShow() {
      this.showCarouselAnimation = true
    },
    handleTabClicked() {
      this.showCarouselAnimation = true
    },
    beforeCarouselImageChanged(index) {
      this.showCarouselAnimation = false
    },
    /**
     * Handler for when image is changed in Carousal
     * @param {Number} changedIndex
     */
    afterCarouselImageChanged(changedIndex) {
      this.updateCarouselInitialState(changedIndex)
    },
    /**
     * Updates Carousel Initial State
     * @param {Number} imageIndex
     */
    updateCarouselInitialState(imageIndex) {
      this.settings = { ...this.settings, initialSlide: imageIndex }
    },
    closeCarousel() {
      this.$bvModal.hide('carousal-modal')
    },
    showThumbnail(point, event) {
      this.activeThumbnail = point.tagged_img_url
      const rect = this.$refs.imageContainer.getBoundingClientRect()
      const pinSize = 12
      const thumbnailHeight = 150

      const pinX = (point.x_percent / 100) * rect.width
      const pinY = (point.y_percent / 100) * rect.height

      const leftPos = pinX - thumbnailHeight / 2
      let topPos = pinY - thumbnailHeight - pinSize

      if (topPos < 0) {
        topPos = pinY + pinSize
      }

      this.thumbnailStyle.left = `${leftPos}px`
      this.thumbnailStyle.top = `${topPos}px`
    },
    hideThumbnail() {
      this.activeThumbnail = null
    },
    prepareFirstLayerInfo() {
      this.first_layer_info = this.firstLayerInfo
      const bedWidth = this.first_layer_info.width
      const bedHeight = this.first_layer_info.height
      const points = this.first_layer_info.points || []

      this.first_layer_info.points = points.map((point) => {
        return {
          ...point,
          x_percent: (point.x / bedWidth) * 100,
          y_percent: 100 - (point.y / bedHeight) * 100, // Invert Y axis because the origin of the points is at the bottom left
        }
      })
      this.carouselItems = this.first_layer_info.points.map((point) => ({
        raw_img_url: point.raw_img_url,
        tagged_img_url: point.tagged_img_url,
      }))
    },
    imageClicked(clickedPoint) {
      const initialSlideIndex = this.carouselItems.findIndex(
        (item) => item.tagged_img_url === clickedPoint.tagged_img_url
      )

      this.updateCarouselInitialState(initialSlideIndex)
      this.carouselKey++
      // Open Carousel Modal
      this.$bvModal.show('carousal-modal')
    },

    toggleHeatmap() {
      this.isHeatmapVisible = !this.isHeatmapVisible
    },
    findNearestPoint(clickX, clickY) {
      let nearestPoint = null
      let smallestDistance = Infinity

      this.first_layer_info['points'].forEach((point) => {
        const distance = this.calculateDistance(clickX, clickY, point.x, point.y)
        if (distance < smallestDistance) {
          smallestDistance = distance
          nearestPoint = point
        }
      })

      return nearestPoint
    },
    calculateDistance(x1, y1, x2, y2) {
      return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))
    },
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

.b-carousel
  padding-bottom: 0.5rem
  .close-button
    padding-top: 6px
    padding-left: 7px
    button
      color: var(--color-text-primary)
      background: transparent
      border: none
      font-size: 22px

.carousel-tabs
  display: flex
  justify-content: center
  height: 480px
  margin-top: 1.25em 
.report-title
  padding-left: 15px

.map-info
  color: var(--color-text-secondary)
  font-weight: 600
  text-align: center
.feedback-button
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
  .image-container
    position: relative
    display: block
    width: 100%

    > img
      border: 1px solid #cac8c8
      width: 100%
      height: auto
      object-fit: contain
      display: block

    .pin
      position: absolute
      width: 12px
      height: 12px
      background-color: #4c9be7
      border-radius: 50%
      transform: translate(-50%, -50%)
      cursor: pointer

      &:after
        content: ''
        position: absolute
        bottom: -10px
        left: 50%
        width: 3px
        height: 10px
        background-color: #4c9be7
        transform: translateX(-50%)

    .thumbnail
      width: 150px
      height: 150px
      position: absolute
      z-index: 2000
      img
        width: 100%
        height: 100%
        object-fit: cover
        border-radius: var(--border-radius-sm)


    .toggle-heatmap
      position: absolute
      top: 2%
      right: 4%
      background: none
      border: none
      cursor: pointer
      z-index: 1
      .fa-eye
        color: #2d2e30
      .fa-eye-slash
        color: #2d2e30

.border-right
  border-right: 1px solid $border-color

.transparent-button
  background-color: transparent
  border-color: #007bff
  color: #007bff
  &:hover
    background-color: rgba(#007bff, 0.1)

.custom-slick-carousel
  width: 600px



@media (max-width: 768px)
  .custom-slick-carousel
    max-width: 80vw
    max-height: 30vh
    img
      border-radius: var(--border-radius-md)
  .file-block-title
    grid-template-columns: 7% 65% 28%

  @media (max-width: 1198px)
    .file-block-title
      grid-template-columns: 7% 65% 28%
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
.fade-in {
  animation: fadeIn 1.2s ease-in-out;
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
.custom-slick-carousel li {
  margin: auto 10px;
}
.custom-slick-carousel .slick-dots {
  top: 24em;
}
.custom-slick-carousel .slick-dots li {
  margin: auto 10px !important;
}
.custom-slick-carousel .slick-dots li button {
  border: 2px solid var(--color-primary) !important;
  background: transparent !important;
}
.custom-slick-carousel .slick-dots li.slick-active button {
  background: var(--color-primary) !important;
}
.custom-slick-carousel .slick-dots li button:before {
  content: none !important;
}
.custom-slick-carousel .slick-prev {
  z-index: 1 !important;
}
.custom-slick-carousel .slick-next {
  z-index: 1 !important;
}
.custom-slick-carousel .slick-prev:before {
  font-size: 44px !important;
  color: var(--color-primary) !important;
  margin-left: -4px !important;
}
.custom-slick-carousel .slick-next:before {
  font-size: 44px !important;
  color: var(--color-primary) !important;
  margin-left: -20px !important;
}
div#carousal-modal {
  animation: swal2-show .3s !important;
  transition: none !important;
}
.modal-dialog.modal-lg {
  transition: none !important
}
.b-carousel {
  background-color: var(--color-surface-primary) !important;
  border-radius: var(--border-radius-lg) !important;
  background: var(--color-surface-secondary) !important;
  @media (min-width: 676px) and (max-width: 991px) {
    width: 667px !important;
    margin-left: -16%;
  }
  @media (min-width: 576px) and (max-width: 675px) {
    width: 600px !important;
    margin-left: -10%;
  }
  @media (min-width: 991px) {
    width: 706px !important;
    left: 3em
  }
  .close-carousel {
    display: flex;
    position: absolute;
    top: 0;
    right: 0;
    justify-content: center;
    width: 1.2em;
    height: 1.2em;
    padding: 0;
    transition: color .1s ease-out;
    border: none;
    border-radius: 0;
    outline: initial;
    background: 0 0;
    color: #ccc !important;
    font-family: serif;
    font-size: 2.5em;
    line-height: 1.2;
    cursor: pointer;
    overflow: hidden;
    font-weight: 100;
    &:hover {
      color: #f27474 !important
    }
  }
}
div#carousal-modal___BV_modal_outer_ {
  z-index: 1100 !important;
}
@media (max-width: 768px) {
  .custom-slick-carousel .slick-prev:before, .custom-slick-carousel .slick-next:before {
    position: relative !important;
    top: 1em !important
  }
}
button.btn.feedback-button.btn-secondary {
  border: 1px solid var(--color-primary) !important
}
</style>
