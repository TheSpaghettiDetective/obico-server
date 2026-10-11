export async function fetchPrintStats(request, params) {
  const groupings = ['day', 'week', 'month', 'year']
  const requestedGrouping = params.group_by.toLowerCase()
  let effectiveGrouping = requestedGrouping

  for (;;) {
    try {
      const response = await request({ ...params, group_by: effectiveGrouping })
      return { response, requestedGrouping, effectiveGrouping }
    } catch (error) {
      const suggestedGrouping = error.response?.data?.suggested_group_by
      if (
        error.response?.status !== 400 ||
        error.response?.data?.code !== 'too_many_stats_buckets' ||
        !groupings.includes(suggestedGrouping) ||
        groupings.indexOf(suggestedGrouping) <= groupings.indexOf(effectiveGrouping)
      ) {
        throw error
      }
      effectiveGrouping = suggestedGrouping
    }
  }
}
