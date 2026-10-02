from django.core.management.base import BaseCommand

from lib.media_urls import MEDIA_URL_FIELDS, transform_urls_on_model
from lib.url_signing import new_signed_url


class Command(BaseCommand):
    help = '(re-)signs all media URLs. Must be run once after updating, and any time the Django SECRET_KEY is rotated'

    def resign_urls(self):
        for obj, url_fields in MEDIA_URL_FIELDS:
            print(f"Resigning {obj.__name__} URLs ({len(obj.objects.all())} rows)...")
            transform_urls_on_model(obj, url_fields, new_signed_url)

    def handle(self, *args, **options):
        self.resign_urls()
