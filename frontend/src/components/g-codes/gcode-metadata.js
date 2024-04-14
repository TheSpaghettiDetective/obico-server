import * as formatters from '@src/lib/formatters'
import i18n from '@src/i18n/i18n.js'

export const gcodeMetadata = [
  {
    name: 'estimated_time',
    faIcon: 'fas fa-clock',
    title: `${i18n.t('Print duration estimate')}`,
    formatter: formatters.humanizedDuration,
  },
  {
    name: 'filament_total',
    faIcon: 'fas fa-ruler-horizontal',
    title: `${i18n.t('Filament usage estimate')}`,
    formatter: formatters.humanizedFilamentUsage,
  },
  {
    name: 'first_layer_bed_temp',
    svgIcon: 'bed-temp',
    title: `${i18n.t('First layer bed temperature')}`,
    formatter: (v) => `${v}°C`,
  },
  {
    name: 'first_layer_extr_temp',
    svgIcon: 'extruder',
    title: `${i18n.t('First layer extruder temperature')}`,
    formatter: (v) => `${v}°C`,
  },
  {
    name: 'first_layer_height',
    faIcon: 'fas fa-layer-group',
    title: `${i18n.t('First layer height')}`,
    formatter: (v) => `${v}mm`,
  },
  {
    name: 'layer_height',
    faIcon: 'fas fa-layer-group',
    title: `${i18n.t('Layer height')}`,
    formatter: (v) => `${v}mm`,
  },
  {
    name: 'object_height',
    faIcon: 'fas fa-ruler-vertical',
    title: `${i18n.t('Object height')}`,
    formatter: (v) => `${Math.round(v)}mm`,
  },
  {
    name: 'filament_type',
    svgIcon: 'filament',
    title: `${i18n.t('Filament type')}`,
    formatter: (v) => v,
  },
  {
    name: 'filament_name',
    svgIcon: 'filament',
    title: `${i18n.t('Filament name')}`,
    formatter: (v) => v,
  },
  {
    name: 'slicer',
    svgIcon: 'slicer-program',
    title: `${i18n.t('Slicer')}`,
    formatter: (v) => v,
  },
  {
    name: 'slicer_version',
    svgIcon: 'slicer-version',
    title: `${i18n.t('Slicer version')}`,
    formatter: (v) => v,
  },
]
