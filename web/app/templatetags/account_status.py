import datetime
from django import template

register = template.Library()

from ..models import *

@register.simple_tag()
def subscription():
    return {
        'is_pro': True,
    }

@register.simple_tag()
def detective_hours():
    return None
