from django import template

register = template.Library()

from ..models import dh_is_unlimited

@register.filter
def dh_badge_num(dh):
    if dh_is_unlimited(dh):
        return'\u221E'
    else:
        return round(dh)
