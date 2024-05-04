from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

class CustomAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        UserModel = get_user_model()
        if request is not None:
            site = get_current_site(request)
            try:
                user = UserModel.objects.get(email=username, site=site)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None