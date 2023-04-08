import * as formatters from '@src/lib/formatters'

export const gcodeMetadata = [
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
    formatter: (v) => `${Math.round(v)}mm`,
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
]
