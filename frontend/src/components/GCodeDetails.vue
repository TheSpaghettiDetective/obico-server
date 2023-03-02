<template>
  <div class="card-container file">
    <div class="file-header" :class="{ 'mb-4': fileDetailsToShow.length > 0 }">
      <div class="icon">
        <i class="fas fa-file-code"></i>
      </div>
      <div class="info overflow-truncated-parent">
        <div class="title overflow-truncated">{{ file.filename }}</div>
        <div
          v-if="file.filesize && file.created_at"
          class="subtitle text-secondary overflow-truncated"
        >
          <div v-if="file.deleted">
            <span class="text-danger">Deleted</span>
          </div>
          <div v-else>
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

export default {
  name: 'GCodeDetails',

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
  },

  data() {
    return {
      extraDetailsVisible: false,
      fileDetailsConfig: [
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
      filtered = this.fileDetailsConfig
        .filter((item) => this.file[item.name])
        .map((item) => {
          return {
            ...item,
            value: item.formatter(this.file[item.name]),
          }
        })
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
  gap: .7rem
  .info
    flex: 1
  .icon
    flex: 0 0 2rem
    text-align: center
    *
      font-size: 2rem
  .title
    font-weight: bold

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
