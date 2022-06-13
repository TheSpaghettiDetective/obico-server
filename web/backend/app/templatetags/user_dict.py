from django import template
from api.serializers import UserSerializer

register = template.Library()

@register.filter
def user_dict(user):
    if user.is_authenticated:
        return UserSerializer(user, many=False).data
    else:
        return None
