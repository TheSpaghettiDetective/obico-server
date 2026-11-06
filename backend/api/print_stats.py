from datetime import datetime, time, timedelta

import pytz
from django.db.models import Case, Count, Max, Sum, Value, When, fields
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError


MAX_STATS_BUCKETS = 2000
STATS_GROUPINGS = ('day', 'week', 'month', 'year')


def next_period_start_after(date_time, period):
    if period == 'day':
        next_start = date_time + timedelta(days=1)
    elif period == 'week':
        # Existing reports start subsequent weeks on Sunday.
        days_until_sunday = 6 - date_time.weekday()
        next_start = date_time + timedelta(days=days_until_sunday or 7)
    elif period == 'month':
        month = date_time.month % 12 + 1
        year = date_time.year + (date_time.month == 12)
        next_start = datetime(year, month, 1, tzinfo=date_time.tzinfo)
    else:
        next_start = datetime(date_time.year + 1, 1, 1, tzinfo=date_time.tzinfo)
    return next_start.replace(hour=0, minute=0, second=0, microsecond=0)


def stats_parameters(params):
    group_by = params.get('group_by', '').lower()
    if group_by not in STATS_GROUPINGS:
        raise ValidationError({'group_by': 'Choose day, week, month, or year.'})

    try:
        tz = pytz.timezone(params.get('timezone', '').replace(' ', '+'))
    except pytz.UnknownTimeZoneError:
        raise ValidationError({'timezone': 'Invalid timezone.'})

    dates = []
    for field, end_of_day in (('from_date', False), ('to_date', True)):
        try:
            date = parse_date(params.get(field, ''))
        except ValueError:
            date = None
        if date is None or date.year == 9999:
            raise ValidationError({field: 'Use a valid YYYY-MM-DD date before year 9999.'})
        try:
            dates.append(timezone.make_aware(
                datetime.combine(date, time(23, 59, 59) if end_of_day else time.min), timezone=tz))
        except pytz.InvalidTimeError:
            raise ValidationError({field: 'Date is ambiguous or does not exist in this timezone.'})
    from_date, to_date = dates
    if from_date > to_date:
        raise ValidationError({'to_date': 'Must be on or after from_date.'})

    periods = [from_date, next_period_start_after(from_date, group_by)]
    while periods[-1] <= to_date:
        if len(periods) - 1 == MAX_STATS_BUCKETS:
            next_index = STATS_GROUPINGS.index(group_by) + 1
            suggested = STATS_GROUPINGS[next_index] if next_index < len(STATS_GROUPINGS) else None
            error = {
                'code': 'too_many_stats_buckets',
                'max_buckets': MAX_STATS_BUCKETS,
            }
            if suggested:
                error['suggested_group_by'] = suggested
            raise ValidationError(error)
        periods.append(next_period_start_after(periods[-1], group_by))
    return tz, from_date, to_date, periods


def summarize_prints(queryset, tz, periods):
    daily_stats = queryset.annotate(date=TruncDay('started_at', tzinfo=tz)).values('date').annotate(
        filament_used=Sum('filament_used'),
        total_print_time=Sum('print_time'),
        longest_print_time=Max('print_time'),
        print_count=Count('*'),
        cancelled_print_count=Sum(Case(
            When(cancelled_at=None, then=Value(0)), default=Value(1), output_field=fields.IntegerField())),
    ).order_by('date')

    counts, times, filament, cancelled = [
        [{'key': start.isoformat(), 'value': 0} for start in periods[:-1]] for _ in range(4)]
    period_index = 0
    longest_print_time = 0
    for day in daily_stats.iterator(chunk_size=2000):
        longest_print_time = max(longest_print_time, day['longest_print_time'] or 0)
        while period_index < len(counts) and day['date'] >= periods[period_index + 1]:
            period_index += 1
        if period_index == len(counts) or day['date'] < periods[period_index]:
            continue
        counts[period_index]['value'] += day['print_count']
        if day['total_print_time'] is not None:
            times[period_index]['value'] += day['total_print_time']
        if day['filament_used'] is not None:
            filament[period_index]['value'] += day['filament_used']
        cancelled[period_index]['value'] += day['cancelled_print_count']

    result = {
        'print_count_groups': counts,
        'print_time_groups': times,
        'filament_used_groups': filament,
        'total_print_count': sum(group['value'] for group in counts),
        'total_print_time': sum(group['value'] for group in times),
        'total_filament_used': sum(group['value'] for group in filament),
        'total_cancelled_print_count': sum(group['value'] for group in cancelled),
        'longest_print_time': longest_print_time,
    }
    result['average_print_time'] = (
        result['total_print_time'] / result['total_print_count'] if result['total_print_count'] else 0)
    result['total_succeeded_print_count'] = result['total_print_count'] - result['total_cancelled_print_count']
    return result
