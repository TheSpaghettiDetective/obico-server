from datetime import datetime, timedelta
from unittest.mock import patch

import pytz
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from api.print_stats import MAX_STATS_BUCKETS
from api.tests import setup_syndicate
from api.viewsets import PrintViewSet
from app.models import Print, Printer, User


class PrintStatsTestCase(TestCase):
    def setUp(self):
        self.tasks = patch('config.celery.celery_app.send_task').start()
        self.addCleanup(patch.stopall)
        self.user = User.objects.create(email='stats@example.invalid', syndicate=setup_syndicate())
        self.printer = Printer.objects.create(user=self.user, auth_token='stats-primary-test')
        self.factory = APIRequestFactory()

    def stats(self, **params):
        query = {'timezone': 'UTC', 'from_date': '2024-01-03', 'to_date': '2024-01-10', 'group_by': 'day'}
        query.update(params)
        request = self.factory.get('/api/v1/prints/stats/', query)
        force_authenticate(request, user=self.user)
        return PrintViewSet.as_view({'get': 'stats'})(request)

    def make_print(self, date, **attrs):
        values = {'user': self.user, 'printer': self.printer, 'ext_id': Print.objects.count() + 1,
                  'filename': 'test.gcode', 'started_at': datetime.fromisoformat(date).replace(tzinfo=pytz.UTC)}
        values.update(attrs)
        return Print.objects.create(**values)

    def test_extreme_empty_report_is_rejected_without_querying_prints(self):
        with patch.object(PrintViewSet, 'get_queryset') as queryset:
            response = self.stats(from_date='1926-01-01', to_date='2025-12-31')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'too_many_stats_buckets')
        self.assertEqual(response.data['suggested_group_by'], 'week')
        queryset.assert_not_called()

    def test_exact_bucket_limit_and_one_over(self):
        start = datetime(2020, 1, 1)
        response = self.stats(from_date='2020-01-01', to_date=(start + timedelta(days=MAX_STATS_BUCKETS - 1)).date().isoformat())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['print_count_groups']), MAX_STATS_BUCKETS)
        response = self.stats(from_date='2020-01-01', to_date=(start + timedelta(days=MAX_STATS_BUCKETS)).date().isoformat())
        self.assertEqual(response.status_code, 400)

    def test_groups_keep_partial_first_week_and_sunday_boundaries(self):
        self.make_print('2024-01-03T12:00:00', print_time=10, filament_used=1)
        self.make_print('2024-01-07T12:00:00', print_time=20, filament_used=2,
                        cancelled_at=timezone.now())
        response = self.stats(group_by='week')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['print_count_groups'], [
            {'key': '2024-01-03T00:00:00+00:00', 'value': 1},
            {'key': '2024-01-07T00:00:00+00:00', 'value': 1},
        ])
        self.assertEqual(response.data['total_print_time'], 30)
        self.assertEqual(response.data['total_filament_used'], 3)
        self.assertEqual(response.data['total_cancelled_print_count'], 1)
        self.assertEqual(response.data['total_succeeded_print_count'], 1)
        self.assertEqual(response.data['average_print_time'], 15)
        self.assertEqual(response.data['longest_print_time'], 20)

    def test_native_mobile_yearly_totals_keep_account_lifetime_history(self):
        self.make_print('2010-01-10T12:00:00', print_time=100, filament_used=10)
        self.make_print('2026-01-10T12:00:00', print_time=200, filament_used=20)
        response = self.stats(from_date='2010-01-01', to_date='2026-10-10', group_by='year')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_print_count'], 2)
        self.assertEqual(response.data['total_print_time'], 300)
        self.assertEqual(len(response.data['print_count_groups']), 17)

    def test_date_filters_deleted_rows_and_printer_filters_are_preserved(self):
        other = Printer.objects.create(user=self.user, auth_token='stats-secondary-test')
        active = self.make_print('2024-01-05T12:00:00', finished_at=timezone.now())
        deleted = self.make_print('2024-01-06T12:00:00', finished_at=timezone.now())
        deleted.delete()
        self.make_print('2024-01-06T13:00:00', printer=other, finished_at=timezone.now())
        self.make_print('2023-12-31T12:00:00', finished_at=timezone.now())
        response = self.stats(filter='finished', **{'filter_by_printer_ids[]': [active.printer_id]})
        self.assertEqual(response.data['total_print_count'], 1)
        response = self.stats(filter='finished', with_deleted='true', **{'filter_by_printer_ids[]': [active.printer_id]})
        self.assertEqual(response.data['total_print_count'], 2)

    def test_all_groupings_include_leap_day_and_null_measurements(self):
        self.make_print('2024-02-29T12:00:00')
        for grouping in ('day', 'week', 'month', 'year', 'Year'):
            with self.subTest(grouping=grouping):
                response = self.stats(from_date='2024-02-28', to_date='2024-03-02', group_by=grouping)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['total_print_count'], 1)
                self.assertEqual(response.data['total_print_time'], 0)
                self.assertEqual(response.data['total_filament_used'], 0)

    def test_invalid_inputs_are_validation_errors(self):
        cases = [{'from_date': ''}, {'to_date': ''}, {'from_date': '2024-02-30'},
                 {'to_date': '9999-12-31'}, {'group_by': 'decade'}, {'group_by': ''},
                 {'timezone': 'not-a-timezone'}, {'timezone': ''},
                 {'from_date': '2024-02-01', 'to_date': '2024-01-01'}]
        for params in cases:
            with self.subTest(params=params):
                self.assertEqual(self.stats(**params).status_code, 400)

    def test_fixed_offset_timezone_with_url_decoded_plus(self):
        self.assertEqual(self.stats(timezone='Etc/GMT 8').status_code, 200)
