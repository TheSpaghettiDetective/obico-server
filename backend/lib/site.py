from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.conf import settings
import re

def build_full_url(url):
    protocol = 'https://' if settings.SITE_USES_HTTPS else 'http://'
    domain_name = Site.objects.first().domain
    normalized_url = re.sub(r'^/', '', url)
    return '{}{}/{}'.format(protocol, domain_name, normalized_url)


this_site_url = build_full_url('')


def url_points_to_this_site(url: str) -> bool:
    """
    Returns True if given 'url' points to this site, else False
    """
    # Using a global variable here avoids calling database each time, but requires
    # restarting the application any time the site domain name is changed.
    #
    # Could also cache in redis to avoid need for restarting if desired, but may
    # add some overhead.
    global this_site_url
    return True if url.startswith(this_site_url) else False
