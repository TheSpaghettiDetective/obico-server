// Credit: https://observablehq.com/@d3/bar-chart

import * as d3 from 'd3'
import moment from 'moment'
import { formatWithoutDaylightSavingShift as format } from '@src/lib/utils'

export const BarChart = (
  data,
  {
    x = (d, i) => i, // given d in data, returns the (ordinal) x-value
    y = (d) => d, // given d in data, returns the (quantitative) y-value
    title, // given d in data, returns the title text
    marginTop = 20, // the top margin, in pixels
    marginRight = 0, // the right margin, in pixels
    marginBottom = 40, // the bottom margin, in pixels
    marginLeft = 40, // the left margin, in pixels
    width = 640, // the outer width of the chart, in pixels
    height = 210, // the outer height of the chart, in pixels
    xDomain, // an array of (ordinal) x-values
    xRange = [marginLeft, width - marginRight], // [left, right]
    xLabelShow = (i) => true, // whether to show the x-axis label
    xLabelRotation = 0, // the rotation of the x-axis label, in degrees
    yType = d3.scaleLinear, // y-scale type
    yDomain, // [ymin, ymax]
    yRange = [height - marginBottom, marginTop], // [bottom, top]
    yTicks = height / 40,
    xPadding = 0.1, // amount of x-range to reserve to separate bars
    yFormat, // a format specifier string for the y-axis
    yTickFormat = null,
    yLabel, // a label for the y-axis
    color = 'currentColor', // bar fill color
  } = {}
) => {
  // Compute values
  const X = d3.map(data, x)
  const Y = d3.map(data, y)

  // Compute default domains, and unique the x-domain
  if (xDomain === undefined) xDomain = X
  if (yDomain === undefined) yDomain = [0, d3.max(Y)]
  xDomain = new d3.InternSet(xDomain)

  // Omit any data not present in the x-domain
  const I = d3.range(X.length).filter((i) => xDomain.has(X[i]))

  // Construct scales, axes, and formats
  const xScale = d3.scaleBand(xDomain, xRange).padding(xPadding)
  const yScale = yType(yDomain, yRange)
  const xAxis = d3.axisBottom(xScale).tickSizeOuter(0)
  const yAxis = d3.axisLeft(yScale).ticks(yTicks, yFormat)
  if (yTickFormat) {
    yAxis.tickFormat(yTickFormat)
  }

  // Compute titles
  if (title === undefined) {
    const formatValue = yScale.tickFormat(100, yFormat)
    title = (i) => `${X[i]}: ${formatValue(Y[i])}`
  } else {
    const O = d3.map(data, (d) => d)
    const T = title
    title = (i) => T(O[i], i, data)
  }

  const svg = d3
    .create('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])
    .attr('style', 'max-width: 100%; height: auto; height: intrinsic;')

  svg
    .append('g')
    .attr('transform', `translate(${marginLeft},0)`)
    .call(yAxis)
    .call((g) =>
      g
        .selectAll('.tick line')
        .clone()
        .attr('x2', width - marginLeft - marginRight)
        .attr('stroke-opacity', 0.1)
    )
    .call((g) => g.selectAll('text').attr('font-size', 11))

  const bar = svg
    .append('g')
    .attr('fill', color)
    .selectAll('rect')
    .data(I)
    .join('rect')
    .attr('x', (i) => xScale(X[i]))
    .attr('y', (i) => yScale(Y[i]))
    .attr('height', (i) => yScale(0) - yScale(Y[i]))
    .attr('width', xScale.bandwidth())
    .attr('rx', 2)

  if (title) bar.append('title').text(title)

  svg
    .append('g')
    .attr('transform', `translate(0,${height - marginBottom})`)
    .call(xAxis)
    .selectAll('text')
    .attr('transform', xLabelRotation ? `translate(-10,0)rotate(-${xLabelRotation})` : '')
    .attr('font-size', 11)
    .call(function (t) {
      t.each(function (d, i) {
        var self = d3.select(this)
        var lines = self.text().split('\r')[0].split('\n') // get the text and split it
        self.text('') // clear it out

        if (xLabelShow(i)) {
          self
            .append('tspan')
            .attr('x', 0)
            .attr('dy', '1em')
            .attr('text-anchor', xLabelRotation ? 'end' : 'middle')
            .text(lines[0])

          if (lines.length === 2) {
            self.append('tspan').attr('x', 0).attr('dy', '1.2em').text(lines[1])
          }
        }
      })
    })

  return svg.node()
}

// Adaptive x-axis labels based on the width of the chart and number of bars
export const xAxisLabelsFormat = (wrapperWidth, barsCount, grouping = 'day', lastDayInDataset) => {
  const barWidth = wrapperWidth / barsCount

  const horizontalLabelRequiredWidth = grouping === 'day' ? 30 : grouping === 'week' ? 70 : 35
  const rotatedLabelRequiredWidth = 20

  let frequency, rotation
  if (barWidth >= horizontalLabelRequiredWidth) {
    frequency = 1
    rotation = 0
  } else {
    frequency = Math.ceil(rotatedLabelRequiredWidth / barWidth)
    rotation = 45
  }

  return {
    frequency,
    rotation,

    value: (d) => {
      const date = moment(d.key)

      let firstLine,
        secondLine = ''
      if (grouping === 'day') {
        firstLine = format(date, 'M/D')
        secondLine = format(date, 'ddd')
      } else if (grouping === 'week') {
        firstLine = format(date, 'M/D')

        const endOfWeek = date.clone().endOf('week')
        const lastDayOfWeek = endOfWeek.isBefore(lastDayInDataset) ? endOfWeek : lastDayInDataset

        firstLine += `-${
          lastDayOfWeek.month() === date.month()
            ? lastDayOfWeek.format('D')
            : lastDayOfWeek.format('M/D')
        }`
        secondLine = lastDayOfWeek.diff(date, 'days') === 6 ? `Week ${date.week()}` : ''
      } else if (grouping === 'month') {
        firstLine = format(date, 'MMM')
        secondLine = format(date, 'YYYY')
      } else {
        firstLine = format(date, 'YYYY')
      }

      let label = firstLine
      if (rotation === 0) {
        label += `\n${secondLine}`
      }

      const uniqueDateKey = format(date, 'M/D/YYYY')
      label += `\r${uniqueDateKey}` // so d3 won't skip same labels

      return label
    },

    shouldShow: (index) => {
      return index % frequency === 0
    },
  }
}
