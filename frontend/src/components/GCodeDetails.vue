<template>
  <div class="card-container file">
    <div
      class="file-header"
      :class="{
        'mb-4': showDetails && fileDetailsToShow.length > 0,
        compact: compactView,
      }"
    >
      <div v-if="showThumbnail">
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
        <div class="title truncated" :title="file.filename">
          {{ file.filename }}
        </div>
        <div v-if="file.filesize || file.deleted" class="subtitle text-secondary truncated-wrapper">
          <div v-if="file.deleted" class="truncated">
            <span class="text-danger">{{$t("Deleted")}}</span>
          </div>
          <div v-else class="truncated">
            <span>{{ file.filesize }}</span>
          </div>
        </div>
      </div>
      <div v-if="showOpenButton && file.id" class="action">
        <b-button
          :variant="openButtonVariant"
          class="custom-button"
          :href="`/g_code_files/cloud/${file.id}/`"
        >
          {{ openButtonText }}
        </b-button>
      </div>
    </div>
    <template v-if="showDetails">
      <!-- First visible lines -->
      <div v-for="item in fileDetailsToShow.slice(0, numberOfVisibleLines)" :key="item.name">
        <div class="line">
          <div class="label">
            <div class="icon">
              <i v-if="item.faIcon" :class="item.faIcon"></i>
              <svg v-else-if="item.svgIcon" width="16" height="16">
                <use :href="`#${item.svgIcon}`" />
              </svg>
            </div>
            <div class="title">{{ item.title }}</div>
          </div>
          <div class="value">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <span v-html="item.value"></span>
          </div>
        </div>
      </div>
      <muted-alert
        v-if="shouldShowDataNotice && fileDetailsToShow.length <= numberOfVisibleLines"
        class="mt-2 mb-1"
      >
        {{$t("Fields above were embedded in the G-Code file by your slicer. Consult your slicer's manual if some fields are not accurate or missing.")}}
      </muted-alert>

      <!-- Hidden lines -->
      <collapsable-details v-if="fileDetailsToShow.length > numberOfVisibleLines">
        <div v-for="item in fileDetailsToShow.slice(numberOfVisibleLines)" :key="item.name">
          <div class="line">
            <div class="label">
              <div class="icon">
                <i v-if="item.faIcon" :class="item.faIcon"></i>
                <svg v-else-if="item.svgIcon" width="16" height="16">
                  <use :href="`#${item.svgIcon}`" />
                </svg>
              </div>
              <div class="title">{{ item.title }}</div>
            </div>
            <div class="value">
              <!-- eslint-disable-next-line vue/no-v-html -->
              <span v-html="item.value"></span>
            </div>
          </div>
        </div>
        <muted-alert
          v-if="shouldShowDataNotice && fileDetailsToShow.length > numberOfVisibleLines"
          class="mt-2 mb-1"
        >
          {{$t("Fields above were embedded in the G-Code file by your slicer. Consult your slicer's manual if some fields are not accurate or missing.")}}
        </muted-alert>
      </collapsable-details>
    </template>
  </div>
</template>

<script>
import MutedAlert from '@src/components/MutedAlert.vue'
import HelpWidget from '@src/components/HelpWidget.vue'
import { gcodeMetadata } from '@src/components/g-codes/gcode-metadata'
import CollapsableDetails from '@src/components/CollapsableDetails.vue'

export default {
  name: 'GCodeDetails',

  components: {
    MutedAlert,
    HelpWidget,
    CollapsableDetails,
  },

  props: {
    file: {
      type: Object,
      required: true,
    },
    showPrintStats: {
      type: Boolean,
      default: false,
    },
    showDetails: {
      type: Boolean,
      default: true,
    },
    showOpenButton: {
      type: Boolean,
      default: false,
    },
    compactView: {
      type: Boolean,
      default: true,
    },
    openButtonVariant: {
      type: String,
      default: 'outline-secondary',
    },
    openButtonText: {
      type: String,
      default: 'Open File',
    },
  },

  data() {
    return {
      numberOfVisibleLines: 3,
    }
  },

  computed: {
    bigThumbnailUrl() {
      return this.file.getBigThumbnailUrl && this.file.getBigThumbnailUrl()
    },
    showThumbnail() {
      return !this.compactView || this.bigThumbnailUrl
    },
    fileDetailsToShow() {
      let result = []
      if (!this.file.deleted && this.file.metadata) {
        result = gcodeMetadata
          .filter((item) => this.file.metadata[item.name])
          .map((item) => {
            return {
              ...item,
              value: item.formatter(this.file.metadata[item.name]),
            }
          })
      }
      if (this.showPrintStats) {
        result.unshift({
          name: 'total_prints',
          faIcon: 'fas fa-hashtag',
          title: `${this.$i18next.t('Total prints')}`,
          value: `
            ${this.file.totalPrints || 0}
            (<span class="text-success">${this.file.successPrints || 0}</span> /
            <span class="text-danger">${this.file.failedPrints || 0}</span>)
          `,
        })
      }
      if (this.file.created_at) {
        result.unshift({
          name: 'created_at',
          faIcon: 'fas fa-calendar-alt',
          title: `${this.$i18next.t('Uploaded')}`,
          value: this.file.created_at.fromNow(),
        })
      }
      return result
    },
    shouldShowDataNotice() {
      return (
        !this.file.analysis &&
        Object.keys(this.file.metadata || {}).length !== 0 &&
        !this.file.deleted
      )
    },
  },
}
</script>

<style lang="sass" scoped>
.file
  display: flex
  flex-direction: column

.file-header
  display: flex
  align-items: center
  gap: 1rem
  .info
    flex: 1
  .icon
    flex: 0 0 2rem
    text-align: center
    *
      font-size: 2rem
  .thumbnail, .thumbnail-placeholder
    width: 100px
    height: 100px
    border-radius: var(--border-radius-md)
    background-color: var(--color-surface-primary)
    display: flex
    align-items: center
    justify-content: center
    overflow: hidden
    img
      height: 100%
      width: auto
      border-radius: 8px
  .title
    font-weight: bold
    font-size: 1.25rem
  .thumbnail-placeholder
    position: relative
    overflow: visible
    svg
      width: 3rem
      height: 3rem
      color: var(--color-background)
    .help
      position: absolute
      top: 4px
      right: 8px

  &.compact
    gap: .7rem
    .thumbnail
      width: 52px
      height: 52px
    .title
      font-size: 1rem

.line
  display: flex
  align-items: center
  justify-content: space-between
  margin-bottm: 6px
  padding: 6px 0
  border-top: 1px solid var(--color-divider-muted)
  gap: .5rem

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
    text-align: right
</style>
