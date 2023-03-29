// Credit: https://observablehq.com/@d3/donut-chart

import * as d3 from 'd3'

export const DonutChart = (
  data,
  {
    name = ([x]) => x, // given d in data, returns the (ordinal) label
    value = ([, y]) => y, // given d in data, returns the (quantitative) value
    totalValue = null, // to show in the middle
    totalValueFormat = ',', // a format specifier for total value
    title, // given d in data, returns the title text
    width = 180, // outer width, in pixels
    height = 180, // outer height, in pixels
    innerRadius = Math.min(width, height) / 3.6, // inner radius of pie, in pixels (non-zero for donut)
    outerRadius = Math.min(width, height) / 2, // outer radius of pie, in pixels
    labelRadius = (innerRadius + outerRadius) / 2, // center radius of labels
    format = ',', // a format specifier for values (in the label)
    names, // array of names (the domain of the color scale)
    colors, // array of colors for names
    stroke = innerRadius > 0 ? 'none' : 'white', // stroke separating widths
    strokeWidth = 10, // width of stroke separating wedges
    strokeLinejoin = 'round', // line join of stroke separating wedges
    padAngle = stroke === 'none' ? 2 / outerRadius : 0, // angular separation between wedges
    emptyState = false, // if true, show empty state
  } = {}
) => {
  // Compute values
  const N = d3.map(data, name)
  const V = d3.map(data, value)
  const I = d3.range(N.length).filter((i) => !isNaN(V[i]))

  // Unique the names
  if (names === undefined) names = N
  names = new d3.InternSet(names)

  // Chose a default color scheme based on cardinality
  if (colors === undefined) colors = d3.schemeSpectral[names.size]
  if (colors === undefined)
    colors = d3.quantize((t) => d3.interpolateSpectral(t * 0.8 + 0.1), names.size)

  // Construct scales
  const color = d3.scaleOrdinal(names, colors)

  // Compute titles
  if (title === undefined) {
    const formatValue = d3.format(format)
    title = (i) => `${formatValue(V[i])}`
  } else {
    const O = d3.map(data, (d) => d)
    const T = title
    title = (i) => T(O[i], i, data)
  }

  // Construct arcs
  const arcs = d3
    .pie()
    .padAngle(padAngle)
    .sort(null)
    .value((i) => V[i])(I)
  const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius)
  const arcLabel = d3.arc().innerRadius(labelRadius).outerRadius(labelRadius)

  const svg = d3
    .create('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [-width / 2, -height / 2, width, height])
    .attr('style', 'max-width: 100%; height: auto; height: intrinsic;')

  svg
    .append('g')
    .attr('stroke', stroke)
    .attr('stroke-width', strokeWidth)
    .attr('stroke-linejoin', strokeLinejoin)
    .selectAll('path')
    .data(arcs)
    .join('path')
    .attr('fill', (d) => color(N[d.data]))
    .attr('d', arc)
    .append('title')
    .text((d) => title(d.data))

  svg
    .append('g')
    .attr('font-family', 'sans-serif')
    .attr('font-size', 14)
    .attr('text-anchor', 'middle')
    .selectAll('text')
    .data(arcs)
    .join('text')
    .attr('transform', (d) => `translate(${arcLabel.centroid(d)})`)
    .selectAll('tspan')
    .data((d) => {
      if (emptyState) return ['0%']
      const lines = `${title(d.data)}`.split(/\n/)
      return d.endAngle - d.startAngle > 0.25 ? lines : lines.slice(0, 1)
    })
    .join('tspan')
    .attr('x', 0)
    .attr('y', (_, i) => `${0.3}em`)
    .attr('font-weight', (_, i) => (i ? null : 'bold'))
    .attr('fill', '#fff')
    .text((d) => d)

  // Total value at the center
  if (totalValue) {
    svg
      .append('text')
      .attr('font-size', 12)
      .attr('dy', '-.75em')
      .attr('text-anchor', 'middle')
      .attr('fill', 'var(--color-text-secondary)')
      .text('Total')

    const formatTotalValue = d3.format(totalValueFormat)

    svg
      .append('text')
      .attr('dy', '.75em')
      .attr('font-size', 14)
      .attr('text-anchor', 'middle')
      .attr('font-weight', 'bold')
      .attr('fill', 'var(--color-text-primary)')
      .text(formatTotalValue(totalValue))
  }

  return Object.assign(svg.node(), { scales: { color } })
}
