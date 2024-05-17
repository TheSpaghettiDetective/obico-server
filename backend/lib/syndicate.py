from django.contrib.sites.shortcuts import get_current_site
from app.models.syndicate_models import Syndicate
from config.settings import SYNDICATES, SITE_USES_HTTPS
import re

def syndicate_from_request(request):
    # 1. user's account syndicate has the highest priority. But I wouldn't be surprised if we later find edge cases that invalidate this rule.
    if request.user.is_authenticated:
      return request.user.syndicate

    # 2. per-request syndicate comes next.
    syndicate_header = request.META.get('HTTP_X_OBICO_SYNDICATE', None)
    if syndicate_header:
      return Syndicate.objects.get(name=syndicate_header)

    # 3. site syndicate is the default.
    return get_current_site(request).syndicates.first()


def settings_for_syndicate(syndicate_name):
    return SYNDICATES[syndicate_name]


SYNDICATE_DOMAIN_CACHE = {}

def build_full_url_for_syndicate(url, syndicate_name):
    global SYNDICATE_DOMAIN_CACHE
    if syndicate_name not in SYNDICATE_DOMAIN_CACHE:
        SYNDICATE_DOMAIN_CACHE[syndicate_name] = Syndicate.objects.get(name=syndicate_name).sites.first().domain

    domain_name = SYNDICATE_DOMAIN_CACHE[syndicate_name]

    protocol = 'https://' if SITE_USES_HTTPS else 'http://'
    normalized_url = re.sub(r'^/', '', url)
    return '{}{}/{}'.format(protocol, domain_name, normalized_url)

