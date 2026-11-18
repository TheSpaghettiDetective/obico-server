from django.core.management.base import BaseCommand

from app.models import GCodeFile
from lib.media_urls import MEDIA_URL_FIELDS, transform_urls_on_model
from lib.url_signing import is_media_url, new_signed_url


def resign_media_url(url):
    # Only a link to a file this server stores is signed. Any other address is left as it is.
    return new_signed_url(url) if is_media_url(url) else url


class Command(BaseCommand):
    help = '(re-)signs all media URLs. Must be run once after updating, and any time the Django SECRET_KEY is rotated'

    def resign_urls(self):
        for obj, url_fields in MEDIA_URL_FIELDS:
            rows = obj.objects.all()
            if obj is GCodeFile:
                # A G-code file that lives on a printer holds the agent's own path to it, not a link to this server.
                rows = rows.filter(resident_printer__isnull=True)
            print(f"Resigning {obj.__name__} URLs ({len(rows)} rows)...")
            transform_urls_on_model(obj, url_fields, resign_media_url, rows=rows)

    def handle(self, *args, **options):
        self.resign_urls()
