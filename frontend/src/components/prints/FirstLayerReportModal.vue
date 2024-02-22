<template>
  <div v-show="isModalOpen" class="content-container">
    <!-- Layer Demo as Modal -->
    <div class="layer-demo-overlay">
      <div class="layer-demo-modal">
        <b-row>
          <div class="close-button mb-1">
            <button @click="$emit('close')">
              <i class="far fa-window-close"></i>
            </button>
          </div>
        </b-row>
        <div class="p-2">
          <b-row>
            <h4 class="mb-4 report-title">First Layer Report</h4>
          </b-row>
          <b-row>
            <b-col lg="6" class="mb-4">
              <!-- File Block Start -->
              <div class="file-block mb-3">
                <!-- File Block 1st row -->
                <b-row>
                  <div class="title">
                    <div class="icon">
                      <i class="fas fa-file-code"></i>
                    </div>
                    <div class="info">
                      <div class="file-name">
                        <span>very-quick-test-print.gcode</span>
                      </div>
                      <div class="file-size">
                        <span>45.5 KB, uploaded 11 days ago</span>
                      </div>
                    </div>

                    <div class="button">
                      <b-button>Open File</b-button>
                    </div>
                  </div>
                </b-row>

                <hr />
                <!-- File Block 2nd row -->
                <b-row>
                  <div class="first-layer-grade">
                    <div class="icon">
                      <i class="fas fa-info dark-icon"></i>
                    </div>
                    <span class="name">First Layer Grade</span>
                    <div class="status" :class="gradeAccent">{{ grade || '&nbsp' }}</div>
                  </div>
                </b-row>
                <hr />
                <!-- File Block 3rd row -->
                <b-row>
                  <div class="first-layer-print-time">
                    <div class="icon">
                      <i class="fas fa-clock dark-icon"></i>
                    </div>
                    <span class="name">First Layer Print Time</span>
                    <div class="status">12%</div>
                  </div>
                </b-row>
                <hr class="mb-0" />
              </div>
              <!-- File Block End -->
              <!-- Notes Block Start -->
              <div class="notes-block mb-4">
                <!-- Notes Block 1st row -->
                <b-row>
                  <span class="title">First Layer Notes</span>
                </b-row>
                <hr />
                <!-- File Block 2nd row -->
                <b-row>
                  <div class="description">
                    <p>
                      You're first layer score is <span class="text-warning">C</span>. The
                      risk for the first layer to cause your point to fail later is LOW.<br />However,
                      if you want a perfect bottom surface finish and structural strength, you
                      can stop the print, perfect your first layer, and restart the print.
                    </p>
                  </div>
                </b-row>
                <hr />
                <!-- File Block 3rd row -->
                <b-row>
                  <div class="info">
                    <p>
                      Grade <span class="text-warning">C</span> usually means one of the
                      following:
                    </p>
                    <ul>
                      <li>Under-extrusion.</li>
                      <li>Over-extrusion.</li>
                      <li>
                        Suboptimal z-offset setting that causes the material to not bont
                        perfectly.
                      </li>
                      <li>
                        Contaminated print bed that causes the material in some areas to
                        slightly bubble or wrap
                      </li>
                      <li>Uneven print bed coupied with suboptimal auto-bed-leveling.</li>
                      <li>Other problems that cause the first layer to have defects.</li>
                    </ul>
                  </div>
                </b-row>
              </div>
              <!-- Notes Block End -->
              <b-button class="mb-3 mt-3" style="width: 100%"
                >View First Layer Timelapse</b-button
              >
              <b-button class="feedback-button" style="width: 100%"
                >Give Feedback About This Report</b-button
              >
            </b-col>
            <!-- Map Section -->
            <b-col lg="6">
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
                    >
                      <div class="close-button mb-5">
                        <button @click="closeCarousel">
                          <i class="far fa-window-close"></i>
                        </button>
                      </div>
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
                          >
                            <vue-slick-carousel
                              v-if="carouselItems.length"
                              :key="carouselKey"
                              ref="slickTagged"
                              v-bind="settings"
                              class="custom-slick-carousel"
                              @afterChange="carouselImageChanged"
                            >
                              <div
                                v-for="(item, index) in carouselItems"
                                :key="`tagged-${index}`"
                              >
                                <img
                                  width="auto"
                                  height="350px"
                                  :src="item.tagged_img_url"
                                  :alt="`Tagged Screenshot ${index + 1}`"
                                />
                              </div>
                            </vue-slick-carousel>
                          </b-tab>

                          <b-tab title="Original Image" title-link-class="carousel-tab">
                            <vue-slick-carousel
                              v-if="carouselItems.length"
                              :key="carouselKey"
                              ref="slickOriginal"
                              v-bind="settings"
                              class="custom-slick-carousel"
                              @afterChange="carouselImageChanged"
                            >
                              <div
                                v-for="(item, index) in carouselItems"
                                :key="`original-${index}`"
                              >
                                <img
                                  width="auto"
                                  height="350px"
                                  :src="item.raw_img_url"
                                  :alt="`Original Screenshot ${index + 1}`"
                                />
                              </div>
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
                Click pins on the g-node map to see snapshots of certain areas of the print.
              </div>
            </b-col>
          </b-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'
import 'vue-loading-overlay/dist/vue-loading.css'
import PageLayout from '@src/components/PageLayout'
import axios from 'axios'

export default {
  name: 'FirstLayerReportModal',
  components: {
    VueSlickCarousel,
    PageLayout,
  },

  data: function () {
    return {
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
    isModalOpen: {
      type: Boolean,
      required: false,
    },
    firstLayerInfo: {
      type: Object,
      required: true,
    },
    grade: {
      type: String,
      required: true,
    },
    gradeAccent: {
      type: String,
      required: true,
    },
  },
  computed: {},
  watch: {
    isModalOpen: function(value) {
      if (!!value) {
        this.$bvModal.show('first-layer-report-modal') 
      } else {
        this.$bvModal.hide('first-layer-report-modal') 
      }
    },
    firstLayerInfo: function(value) {
      if (!!value) {
        this.prepareFirstLayerInfo()
      }
    }
  },

  mounted() {
    const heatmapImage = new Image()
    heatmapImage.src = this.first_layer_info.heatmap_img_url
  },

  methods: {
    /**
     * Handler for when image is changed in Carousal
     * @param {Number} changedIndex
     */
    carouselImageChanged(changedIndex) {
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
          y_percent: (point.y / bedHeight) * 100,
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
.layer-demo-overlay
  position: fixed
  z-index: 1000
  top: 0
  left: 0
  overflow: auto
  height: 100vh
  background-color: rgba(0, 0, 0, 0.5)
.layer-demo-modal
  border-radius: var(--border-radius-lg)
  padding: auto 1em !important
  padding: 10px 20px
  background-color: var(--color-surface-secondary)
  margin: 2em 2em 0 8em
  .close-button
    padding-top: 6px
    padding-left: 7px
    button
      color: white
      background: transparent
      border: none
      font-size: 22px
.b-carousel
  padding-bottom: 0.5rem
  .close-button
    padding-top: 6px
    padding-left: 7px
    button
      color: white
      background: transparent
      border: none

.carousel-tabs
  display: flex
  justify-content: center
  height: 480px
.report-title
  padding-left: 15px

.map-info
  color: var(--color-text-secondary)
  font-weight: 600
  text-align: center
.feedback-button
  color: var(--color-primary)
  border-color: var(--color-primary)
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
.content-container
  margin: 0 auto
  position: relative
  .card-description
    border-radius: var(--border-radius-lg)
  .card-map
    border-radius: var(--border-radius-lg)
    background: white
  .card-footer
    border-radius: var(--border-radius-lg)
  .image-container
    padding: 3.5em
    position: relative
    display: block
    width: 100%

    > img
      border: 1px solid black
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
    .carousel-overlay
      display: flex
      justify-content: center
      align-items: center
      position: fixed
      top: 0
      left: 0
      width: 100vw
      height: 100vh
      background-color: rgba(0, 0, 0, 0.5)
      z-index: 1050
      .container
        background: var(--color-surface-primary)
        width: 50%
        display: flex
        border-radius: var(--border-radius-lg)
        justify-content: center

    .close-carousel
      position: absolute
      top: 1rem
      right: 1rem
      border: none
      background: none
      color: white
      font-size: 1.5rem
      cursor: pointer
      z-index: 1050

    .toggle-heatmap
      position: absolute
      top: 65px
      right: 70px
      background: none
      border: none
      cursor: pointer
      .fa-eye
        color: #495b71
      .fa-eye-slash
        color: #495b71

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
.b-carousel {
  background-color: var(--color-surface-primary) !important;
  border-radius: var(--border-radius-lg) !important;
  z-index: 11;
  @media (min-width: 676px) and (max-width: 991px) {
    width: 667px !important;
    margin-left: -16%;
  }
  @media (min-width: 576px) and (max-width: 675px) {
    width: 600px !important;
    margin-left: -10%;
  }
  @media (min-width: 992px) {
    width: 706px !important;
  }
}
</style>
