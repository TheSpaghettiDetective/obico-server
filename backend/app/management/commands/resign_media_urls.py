import os

from django.conf import settings
from django.core.management.base import BaseCommand

from app.models import GCodeFile
from lib.media_urls import MEDIA_URL_FIELDS, transform_urls_on_model
from lib.url_signing import calculate_hmac_digest, is_media_url, new_signed_url

# Records which key last signed the stored links. It holds a digest made with the key, not the key.
SIGNED_WITH_PATH = os.path.join(settings.BASE_DIR, '.media_urls_signed_with')


def resign_media_url(url):
    # Only a link to a file this server stores is signed. Any other address is left as it is.
    return new_signed_url(url) if is_media_url(url) else url


def current_key_fingerprint():
    return calculate_hmac_digest('resign_media_urls')


class Command(BaseCommand):
    help = '(re-)signs all media URLs. Must be run once after updating, and any time the Django SECRET_KEY is rotated'

    def add_arguments(self, parser):
        parser.add_argument('--once-per-key', action='store_true',
                            help='Do nothing if the stored links were already signed with the current SECRET_KEY. Run at every start.')

    def resign_urls(self):
        for obj, url_fields in MEDIA_URL_FIELDS:
            rows = obj.objects.all()
            if obj is GCodeFile:
                # A G-code file that lives on a printer holds the agent's own path to it, not a link to this server.
                rows = rows.filter(resident_printer__isnull=True)
            print(f"Resigning {obj.__name__} URLs ({rows.count()} rows)...")
            transform_urls_on_model(obj, url_fields, resign_media_url, rows=rows)

    def handle(self, *args, **options):
        if options['once_per_key'] and os.path.exists(SIGNED_WITH_PATH):
            with open(SIGNED_WITH_PATH) as f:
                if f.read() == current_key_fingerprint():
                    print('Media URLs are already signed with the current SECRET_KEY.')
                    return
        self.resign_urls()
        with open(SIGNED_WITH_PATH, 'w') as f:
            f.write(current_key_fingerprint())
