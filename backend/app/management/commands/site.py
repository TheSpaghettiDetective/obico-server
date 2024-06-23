from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.syndicate_models import Syndicate
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Utilities for advanced django site management.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--add',
            type=str,
            metavar='{ip:port or fqdn:port}',
            help='Add a site. The argument is the Django site domain, such as "example.com:3334". Note: NO http:// or https:// otherwise it will NOT work.',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix a site if the server returns a 500. This is necessary for upgrading servers created before June 5th, 2024.',
        )

    def handle(self, *args, **options):
        syndicate, _ = Syndicate.objects.get_or_create(name="base")

        if options['add']:
            self.add_site(syndicate, options['add'])
        elif options['fix']:
            self.fix_site(syndicate)
        else:
            self.print_help("", "site")

    def add_site(self, syndicate, site_domain):
        with transaction.atomic():

            # If a site domain is provided, add the site
            if site_domain:
                site, created = Site.objects.get_or_create(domain=site_domain, defaults={'name': site_domain})
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Site "{site_domain}" created.'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Site "{site_domain}" already exists.'))

                # Link the site to the syndicate if not already linked
                if not site.syndicates.filter(id=syndicate.id).exists():
                    site.syndicates.add(syndicate)

    def fix_site(self, syndicate):
        with transaction.atomic():
            # Link all sites without a syndicate to the syndicate
            sites_without_syndicate = Site.objects.filter(syndicates__isnull=True)

            for site in sites_without_syndicate:
                site.syndicates.add(syndicate)

        self.stdout.write(self.style.SUCCESS('Sites fixed successfully.'))
