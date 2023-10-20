from typing import List

from django.core.management.base import BaseCommand

from app.models import Print, PrinterEvent, GCodeFile, models
from lib.url_signing import new_signed_url
from lib.utils import printProgressBar


class Command(BaseCommand):
    help = '(re-)signs all media URLs. Must be run once after updating, and any time the Django SECRET_KEY is rotated'

    @staticmethod
    def _resign_urls_on_model(obj: models.Model, url_fields: List[str]):
        changed = False
        total_rows = len(obj.objects.all())
        print(f"Resigning {obj.__name__} URLs ({total_rows} rows)...")
        for idx, row in enumerate(obj.objects.all()):
            for url_field in url_fields:
                url = getattr(row, url_field)
                if url:
                    setattr(row, url_field, new_signed_url(url))
                    changed = True
            if changed:
                row.save()
            if idx % 20 == 0:
                printProgressBar(idx + 1, total_rows)
        printProgressBar(1, 1)

    def resign_urls(self):
        self._resign_urls_on_model(
            obj=GCodeFile,  # type: ignore
            url_fields=['url', 'thumbnail1_url', 'thumbnail2_url', 'thumbnail3_url']
        )
        self._resign_urls_on_model(
            obj=Print,  # type: ignore
            url_fields=['video_url', 'tagged_video_url', 'poster_url']
        )
        self._resign_urls_on_model(
            obj=PrinterEvent,  # type: ignore
            url_fields=['image_url']
        )

    def handle(self, *args, **options):
        self.resign_urls()
