# from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

class CustomAuthenticationBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
            password = kwargs.get('password')
        self.site = get_current_site(request)
        self.email = username
        UserModel = get_user_model()
        try:
            # Retrieve user based on email and site
            user = UserModel.objects.get(email=username, site=self.site)
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """
        Overrides the get_user method to allow users to log in using their email address.
        """
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
