from django.core.management.base import BaseCommand, CommandError

from lib.media_urls import MEDIA_URL_FIELDS, transform_urls_on_model
from lib.url_signing import normalize_origin, rewrite_url_origin


class Command(BaseCommand):
    help = ('Rewrites the scheme and host of all media URLs that point at --old-origin so they point at --new-origin instead. '
            'Run this after the server address has changed, so that previously stored timelapses, snapshots, etc. keep working. '
            'URLs on any other origin, and relative URLs, are left untouched. Query strings (including digests) are preserved.')

    def add_arguments(self, parser):
        parser.add_argument('--old-origin', required=True, help='Origin currently stored in the media URLs, e.g. "http://192.168.1.50:3334"')
        parser.add_argument('--new-origin', required=True, help='Origin to rewrite them to, e.g. "https://obico.example.com"')
        parser.add_argument('--dry-run', action='store_true', help='Only report how many URLs would be rewritten. Nothing is saved.')

    def rewrite_urls(self, old_origin, new_origin, dry_run=False):
        for obj, url_fields in MEDIA_URL_FIELDS:
            print(f"Rewriting {obj.__name__} URLs ({len(obj.objects.all())} rows)...")
            changed = transform_urls_on_model(
                obj, url_fields, lambda url: rewrite_url_origin(url, old_origin, new_origin), save=not dry_run)
            print(f"{obj.__name__}: {changed} URLs {'would be rewritten (dry run)' if dry_run else 'rewritten'}")

    def handle(self, *args, **options):
        try:
            old_origin = normalize_origin(options['old_origin'])
            new_origin = normalize_origin(options['new_origin'])
        except ValueError as e:
            raise CommandError(str(e))
        if options['dry_run']:
            print("Dry run: no changes will be saved.")
        self.rewrite_urls(old_origin, new_origin, dry_run=options['dry_run'])
