<template>
  <div class="card-container file">
    <div
      class="file-header"
      :class="{
        'mb-4': fileDetailsToShow.length > 0,
        compact: compactView,
      }"
    >
      <div v-if="thumbnailUrl" class="thumbnail">
        <img :src="thumbnailUrl" />
      </div>
      <div v-else class="icon">
        <i class="fas fa-file-code"></i>
      </div>
      <div class="info overflow-truncated-parent">
        <div class="title overflow-truncated">
          {{ file.filename }}
        </div>
        <div
          v-if="file.filesize && file.created_at"
          class="subtitle text-secondary overflow-truncated-parent"
        >
          <div v-if="file.deleted" class="overflow-truncated">
            <span class="text-danger">Deleted</span>
          </div>
          <div v-else class="overflow-truncated">
            <span>{{ file.filesize }}</span>
            <span v-if="file.created_at">, uploaded {{ file.created_at.fromNow() }}</span>
          </div>
        </div>
      </div>
      <div v-if="showOpenButton && file.id" class="action">
        <a class="btn btn-secondary" :href="`/g_code_files/cloud/${file.id}/`">Open</a>
      </div>
    </div>
    <!-- First visible lines -->
    <div v-for="item in fileDetailsToShow.slice(0, 4)" :key="item.name">
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
    <muted-alert v-if="shouldShowDataNotice && fileDetailsToShow.length <= 4" class="mt-2 mb-1">
      Fields above were embedded in the G-Code file by your slicer. Consult your slicer's manual if
      some fields are not accurate or missing.
    </muted-alert>

    <!-- Hidden lines -->
    <b-collapse id="g-code-details-collapsible" v-model="extraDetailsVisible">
      <div v-for="item in fileDetailsToShow.slice(4)" :key="item.name">
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
      <muted-alert v-if="shouldShowDataNotice && fileDetailsToShow.length > 4" class="mt-2 mb-1">
        Fields above were embedded in the G-Code file by your slicer. Consult your slicer's manual
        if some fields are not accurate or missing.
      </muted-alert>
    </b-collapse>
    <!-- Collapse toggle -->
    <button
      v-if="fileDetailsToShow.length > 4"
      class="collapse-toggle"
      :class="extraDetailsVisible ? 'opened' : 'closed'"
      :aria-expanded="extraDetailsVisible ? 'true' : 'false'"
      aria-controls="g-code-details-collapsible"
      @click="extraDetailsVisible = !extraDetailsVisible"
    >
      <span v-if="extraDetailsVisible">Show less</span>
      <span v-else>Show more</span>
      <i class="fas fa-chevron-down" :class="{ rotated: extraDetailsVisible }"></i>
    </button>
  </div>
</template>

<script>
import * as formatters from '@src/lib/formatters'
import MutedAlert from '@src/components/MutedAlert.vue'

export default {
  name: 'GCodeDetails',

  components: {
    MutedAlert,
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
    showOpenButton: {
      type: Boolean,
      default: false,
    },
    compactView: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      extraDetailsVisible: false,
      thumbnailUrl: null,
      fileDetailsConfig: [
        {
          name: 'estimated_time',
          faIcon: 'fas fa-clock',
          title: 'Print duration estimate',
          formatter: formatters.humanizedDuration,
        },
        {
          name: 'filament_total',
          faIcon: 'fas fa-ruler-horizontal',
          title: 'Filament usage estimate',
          formatter: formatters.humanizedFilamentUsage,
        },
        {
          name: 'first_layer_bed_temp',
          svgIcon: 'bed-temp',
          title: 'First layer bed temperature',
          formatter: (v) => `${v}°C`,
        },
        {
          name: 'first_layer_extr_temp',
          svgIcon: 'extruder',
          title: 'First layer extruder temperature',
          formatter: (v) => `${v}°C`,
        },
        {
          name: 'first_layer_height',
          faIcon: 'fas fa-layer-group',
          title: 'First layer height',
          formatter: (v) => `${v}mm`,
        },
        {
          name: 'layer_height',
          faIcon: 'fas fa-layer-group',
          title: 'Layer height',
          formatter: (v) => `${v}mm`,
        },
        {
          name: 'object_height',
          faIcon: 'fas fa-ruler-vertical',
          title: 'Object height',
          formatter: (v) => `${v}mm`,
        },
        {
          name: 'filament_type',
          svgIcon: 'filament',
          title: 'Filament type',
          formatter: (v) => v,
        },
        {
          name: 'filament_name',
          svgIcon: 'filament',
          title: 'Filament name',
          formatter: (v) => v,
        },
        {
          name: 'slicer',
          svgIcon: 'slicer-program',
          title: 'Slicer',
          formatter: (v) => v,
        },
        {
          name: 'slicer_version',
          svgIcon: 'slicer-version',
          title: 'Slicer version',
          formatter: (v) => v,
        },
      ],
    }
  },

  computed: {
    fileDetailsToShow() {
      let filtered = []
      if (!this.file.deleted) {
        filtered = this.fileDetailsConfig
          .filter((item) => this.file[item.name])
          .map((item) => {
            return {
              ...item,
              value: item.formatter(this.file[item.name]),
            }
          })
      }
      if (this.showPrintStats) {
        filtered.unshift({
          name: 'total_prints',
          faIcon: 'fas fa-hashtag',
          title: 'Total prints',
          value: `
            ${this.file.totalPrints || 0}
            (<span class="text-success">${this.file.successPrints || 0}</span> /
            <span class="text-danger">${this.file.failedPrints || 0}</span>)
          `,
        })
      }
      return filtered
    },
    shouldShowDataNotice() {
      return (
        !this.file.analysis &&
        (this.fileDetailsToShow.length > 1 ||
          (this.fileDetailsToShow.length === 1 &&
            this.fileDetailsToShow[0].name !== 'total_prints'))
      )
    },
  },

  created() {
    let thumbnailProps = ['thumbnail1_url', 'thumbnail2_url', 'thumbnail3_url']
    for (const t of thumbnailProps) {
      if (this.file[t]) {
        this.thumbnailUrl = this.file[t]
        break
      }
    }
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
  .thumbnail
    width: 100px
    height: 100px
    border-radius: var(--border-radius-md)
    padding: 2px
    background-color: var(--color-surface-primary)
    display: flex
    align-items: center
    justify-content: center
    overflow: hidden
    img
      width: 100%
      height: 100%
  .title
    font-weight: bold
    font-size: 1.25rem

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

.collapse-toggle
  font-weight: bold
  display: flex
  align-items: center
  justify-content: center
  gap: .5rem
  background: none
  border: none
  color: var(--color-text-primary)
  margin-top: .5rem

  i
    transition: all .3s ease-in-out
    &.rotated
      transform: rotate(180deg)
</style>
