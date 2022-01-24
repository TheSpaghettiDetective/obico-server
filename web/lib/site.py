from django.contrib.sites.models import Site
from django.contrib.sites import models as sites_models
from django.conf import settings
from django.db.models.signals import post_delete, post_save
import re


def build_full_url(url):
    protocol = 'https://' if settings.SITE_USES_HTTPS else 'http://'
    domain_name = Site.objects.get_current().domain
    normalized_url = re.sub(r'^/', '', url)
    return '{}{}/{}'.format(protocol, domain_name, normalized_url)


def fill_sites_cache(sender, **kwargs):
    if settings.SITE_DOMAIN:
        sites_models.SITE_CACHE[settings.SITE_ID] = Site(
            pk=settings.SITE_ID,
            domain=settings.SITE_DOMAIN,
            name=settings.SITE_NAME
        )


post_delete.connect(fill_sites_cache, sender=Site)
post_save.connect(fill_sites_cache, sender=Site)
fill_sites_cache(None)
