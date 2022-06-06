#!/usr/bin/env python
import csv
import sys
from django.core.management.base import BaseCommand, CommandError

from app.models import *


class Command(BaseCommand):
    help = 'Extract prints from history table'

    def handle(self, *args, **options):
        header_written = False
        for pprint in Print.objects.all(force_visibility=True).iterator():
            alerts_hist = HistoricalPrinter.objects.filter(id=pprint.printer_id, current_print_started_at=pprint.started_at, current_print_alerted_at__isnull=False).order_by('-history_id')
            acks_hist = HistoricalPrinter.objects.filter(id=pprint.printer_id, current_print_started_at=pprint.started_at, alert_acknowledged_at__isnull=False).order_by('-history_id')
            alerted_at = alerts_hist[0].current_print_alerted_at if len(alerts_hist) > 0 else None
            acked_at = acks_hist[0].alert_acknowledged_at if len(acks_hist) > 0 else None
            row = dict(
                print_id=pprint.id,
                started=pprint.started_at,
                finished=pprint.finished_at,
                cancelled=pprint.cancelled_at,
                alerted=alerted_at,
                acked=acked_at,
                started_secs=int(pprint.started_at.timestamp()),
                finished_secs=int(pprint.finished_at.timestamp()) if pprint.finished_at else '',
                cancelled_secs=int(pprint.cancelled_at.timestamp()) if pprint.cancelled_at else '',
                alerted_secs=int(alerted_at.timestamp()) if alerted_at else '',
                acked_secs=int(acked_at.timestamp()) if acked_at else '',
                video_url=pprint.video_url,
                tagged_video_url=pprint.tagged_video_url,
                prediction_json_url=pprint.prediction_json_url,
            )
            if not header_written:
                w = csv.DictWriter(sys.stdout, row.keys())
                w.writeheader()
                header_written = True
            w.writerow(row)
