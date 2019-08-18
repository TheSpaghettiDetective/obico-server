from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.conf import settings
import re

def build_full_url(url, request=None):
    protocol = 'https://' if settings.SITE_USES_HTTPS else 'http://'

    if request:
        domain_name = RequestSite(request).domain
    else:
        domain_name = Site.objects.get_current().domain

    normalized_url = re.sub(r'^/', '', url)
    return '{}{}/{}'.format(protocol, domain_name, normalized_url)
