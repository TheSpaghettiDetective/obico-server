// Credit: https://observablehq.com/@d3/bar-chart

import * as d3 from 'd3'
import moment from 'moment'

export const BarChart = (
  data,
  {
    x = (d, i) => i, // given d in data, returns the (ordinal) x-value
    y = (d) => d, // given d in data, returns the (quantitative) y-value
    title, // given d in data, returns the title text
    marginTop = 20, // the top margin, in pixels
    marginRight = 0, // the right margin, in pixels
    marginBottom = 40, // the bottom margin, in pixels
    marginLeft = 30, // the left margin, in pixels
    width = 640, // the outer width of the chart, in pixels
    height = 210, // the outer height of the chart, in pixels
    xDomain, // an array of (ordinal) x-values
    xRange = [marginLeft, width - marginRight], // [left, right]
    xLabelShow = (d) => true, // whether to show the x-axis label
    xLabelRotation = 0, // the rotation of the x-axis label, in degrees
    yType = d3.scaleLinear, // y-scale type
    yDomain, // [ymin, ymax]
    yRange = [height - marginBottom, marginTop], // [bottom, top]
    yTicks = height / 40,
    xPadding = 0.1, // amount of x-range to reserve to separate bars
    yFormat, // a format specifier string for the y-axis
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

        if (xLabelShow(data[i])) {
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
export const xAxisLabelsFormat = (wrapperWidth, barsCount) => {
  const pxBarWidth = wrapperWidth / barsCount
  const pxMinWidthForHorizontalLabel = 30
  const pxMinWidthForRotatedLabel = 18

  let frequency, rotation
  if (pxBarWidth >= pxMinWidthForHorizontalLabel) {
    frequency = 'daily'
    rotation = 0
  } else if (pxBarWidth >= pxMinWidthForRotatedLabel) {
    frequency = 'daily'
    rotation = 45
  } else if (pxBarWidth * 7 >= pxMinWidthForRotatedLabel) {
    frequency = 'weekly'
    rotation = 45
  } else if (pxBarWidth * 30 >= pxMinWidthForRotatedLabel) {
    frequency = 'monthly'
    rotation = 45
  } else {
    frequency = 'yearly'
    rotation = 45
  }

  return {
    frequency,
    rotation,

    value: (d) => {
      const date = moment(d.key)

      const isFirstDayOfYear = date.month() === 0 && date.date() === 1
      const isFirstWeekOfYear = date.week() === 1
      const isFirstMonthOfYear = date.month() === 0
      const renderYear =
        frequency === 'yearly' ||
        (frequency === 'monthly' && isFirstMonthOfYear) ||
        (frequency === 'weekly' && isFirstWeekOfYear) ||
        (frequency === 'daily' && isFirstDayOfYear)
      const renderMonth = frequency === 'monthly' && !renderYear

      let label = renderYear
        ? date.month() === 11
          ? (parseInt(date.format('YYYY')) + 1).toString()
          : date.format('YYYY')
        : renderMonth
        ? date.format('MMM')
        : date.format('M/D')

      if (rotation === 0) {
        label += `\n${date.format('ddd')}` // add weekday as a second line
      }

      const uniqueDateKey = date.format('M/D/YYYY')
      label += `\r${uniqueDateKey}` // so d3 won't skip same labels

      return label
    },

    shouldShow: (d) => {
      const date = moment(d.key)
      if (frequency === 'daily') {
        return true
      } else if (frequency === 'monthly') {
        return date.date() === 1
      } else if (frequency === 'weekly') {
        return date.day() === 0
      } else if (frequency === 'yearly') {
        return date.month() === 0 && date.date() === 1
      }
    },
  }
}
