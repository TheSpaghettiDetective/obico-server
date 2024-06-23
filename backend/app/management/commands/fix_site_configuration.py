from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.syndicate_models import Syndicate
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Add a syndicate if it does not exist and link it to all sites without a syndicate. Optionally add a site.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site',
            type=str,
            help='Optional site domain to add.',
        )

    def handle(self, *args, **options):
        syndicate_name = "base"
        site_domain = options['site']

        with transaction.atomic():
            # Ensure the syndicate exists
            syndicate, _ = Syndicate.objects.get_or_create(name=syndicate_name)

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

            # Link all sites without a syndicate to the syndicate
            sites_without_syndicate = Site.objects.filter(syndicates__isnull=True)

            for site in sites_without_syndicate:
                site.syndicates.add(syndicate)

        self.stdout.write(self.style.SUCCESS('Operation completed successfully.'))
