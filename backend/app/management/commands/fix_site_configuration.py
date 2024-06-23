from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.syndicate_models import Syndicate
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Add a syndicate if it does not exist and link it to all sites without a syndicate.'

    def handle(self, *args, **options):
        syndicate_name = "base"
        
        with transaction.atomic():
            # Check if the syndicate exists, if not create it
            syndicate, created = Syndicate.objects.get_or_create(name=syndicate_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Syndicate "{syndicate_name}" created.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Syndicate "{syndicate_name}" already exists.'))

            # Find all sites without a syndicate and link them to the created/found syndicate
            sites_without_syndicate = Site.objects.filter(syndicates__isnull=True)

            for site in sites_without_syndicate:
                site.syndicates.add(syndicate)
                self.stdout.write(self.style.SUCCESS(f'Linked site "{site.name}" to syndicate "{syndicate_name}".'))

        self.stdout.write(self.style.SUCCESS('Operation completed successfully.'))
