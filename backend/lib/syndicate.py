"""Which syndicate and which brand a request gets.

A syndicate is a set of accounts (app.models.Syndicate), picked by the request's
host (SiteSyndicate). A brand is only how pages and emails look (settings.BRANDS):
picked per request, never stored, never used to pick accounts.

Until settings.SYNDICATE_MISMATCH is 'refuse', the syndicate follows the order the
server always had: the signed-in account's, then the X-Obico-Syndicate header's,
then the host's. app.middleware.syndicate_mismatch reports every request where
they disagree, so the switch to the host alone is made on evidence."""
import re

from django.conf import settings

from app.models.syndicate_models import Syndicate, SiteSyndicate
from config.settings import SITE_USES_HTTPS

BASE = 'base'
JUSPRIN_V1_BRAND = 'jusprin'
# JusPrin v1's built-in browser. JusPrin 2 names OrcaSlicer's release after its
# own (jusprin/v2/app_version.py), and its pages open in a browser of its own.
JUSPRIN_V1_USER_AGENT = re.compile(r'^JusPrin(?!.*\sOrcaSlicer/)')


def host_syndicate(request):
    # request.site is TopDomainMatchingCurrentSiteMiddleware's: an unknown host
    # gets the first site.
    return SiteSyndicate.objects.select_related('syndicate').get(site_id=request.site.id).syndicate


def header_syndicate_name(request):
    """The name a mobile app's X-Obico-Syndicate header gives, carried over by
    app.middleware.syndicate_header's cookie. A brand's name, and in the old
    order also a syndicate's."""
    return request.META.get('HTTP_X_OBICO_SYNDICATE') or None


def syndicate_from_request(request):
    if settings.SYNDICATE_MISMATCH == 'log':
        if request.user.is_authenticated:
            return request.user.syndicate
        name = header_syndicate_name(request)
        syndicate = Syndicate.objects.filter(name=name).first() if name else None
        if syndicate:
            return syndicate
    return host_syndicate(request)


def brand_from_request(request):
    """Kingroon's and JusPrin 2's hosts show their own brand. On Obico's hosts,
    JusPrin v1 shows its brand, a mobile app the brand its header names, and
    anything else the request's syndicate's brand."""
    host = host_syndicate(request)
    if host.name != BASE:
        return brand_of_syndicate(host.name)
    if JUSPRIN_V1_USER_AGENT.match(request.META.get('HTTP_USER_AGENT', '')):
        return JUSPRIN_V1_BRAND
    header = header_syndicate_name(request)
    if header in settings.BRANDS:
        return header
    return brand_of_syndicate(syndicate_from_request(request).name)


def brand_of_syndicate(syndicate_name):
    return settings.SYNDICATES[syndicate_name]['brand']


def brand_settings(brand):
    return settings.BRANDS[brand]


SYNDICATE_DOMAIN_CACHE = {}

def build_full_url_for_syndicate(url, syndicate_name):
    global SYNDICATE_DOMAIN_CACHE
    if syndicate_name not in SYNDICATE_DOMAIN_CACHE:
        # The syndicate's first site by domain, as Site's ordering made it when
        # sites were a many-to-many.
        SYNDICATE_DOMAIN_CACHE[syndicate_name] = SiteSyndicate.objects.filter(
            syndicate__name=syndicate_name).order_by('site__domain').first().site.domain

    domain_name = SYNDICATE_DOMAIN_CACHE[syndicate_name]

    protocol = 'https://' if SITE_USES_HTTPS else 'http://'
    normalized_url = re.sub(r'^/', '', url)
    return '{}{}/{}'.format(protocol, domain_name, normalized_url)
