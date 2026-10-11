import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

// Load this Vue ES module without changing the frontend package's module type.
const source = await readFile(new URL('../src/lib/printStats.js', import.meta.url), 'utf8')
const { fetchPrintStats } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`)
const tooMany = (suggested) => ({
  response: { status: 400, data: { code: 'too_many_stats_buckets', suggested_group_by: suggested } },
})
const params = Object.freeze({
  group_by: 'Day', from_date: '1926-01-01', to_date: '2025-12-31',
  timezone: 'America/Los_Angeles', with_deleted: 'true', filter: 'finished',
  'filter_by_printer_ids[]': [10, 11],
})
const calls = []
const result = await fetchPrintStats(async (query) => {
  calls.push(query)
  if (query.group_by === 'day') throw tooMany('week')
  if (query.group_by === 'week') throw tooMany('month')
  return { data: { total_print_count: 42 } }
}, params)
assert.deepEqual(calls.map((query) => query.group_by), ['day', 'week', 'month'])
for (const query of calls) assert.deepEqual(query, { ...params, group_by: query.group_by })
assert.equal(params.group_by, 'Day')
assert.equal(result.requestedGrouping, 'day')
assert.equal(result.effectiveGrouping, 'month')
assert.equal(result.response.data.total_print_count, 42)

let annualCalls = 0
const annual = await fetchPrintStats(async (query) => {
  annualCalls++
  assert.equal(query.group_by, 'year')
  return { data: { total_print_count: 42 } }
}, { ...params, group_by: 'Year' })
assert.equal(annualCalls, 1)
assert.equal(annual.effectiveGrouping, 'year')

const errors = [
  { response: { status: 500 } },
  { response: { status: 400, data: { code: 'invalid_date' } } },
  tooMany('day'), tooMany('decade'), tooMany(undefined), new Error('offline'),
]
for (const error of errors) {
  let attempts = 0
  await assert.rejects(fetchPrintStats(async () => { attempts++; throw error }, params),
    (actual) => actual === error)
  assert.equal(attempts, 1)
}
console.log('8 frontend statistics scenarios passed: bounded retries, annual response, and 6 error cases.')
